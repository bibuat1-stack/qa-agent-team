#!/usr/bin/env python3
"""在当前桌面打开直连有头 Chromium，使用固定配置目录，不走 8791。

用法：
  QA_OWNER=<号名> DISPLAY=:<显示号> python3 /workspace/qa/bin/open_direct_headed.py [网址]
  QA_OWNER=<号名> DISPLAY=:<显示号> python3 /workspace/qa/bin/open_direct_headed.py --once [网址]
  QA_OWNER=<号名> DISPLAY=:<显示号> python3 /workspace/qa/bin/open_direct_headed.py --width 1280 --height 800 [网址]

默认一直开着，关窗口或进程后退出。--once 只打开到 load 就关，用来核对启动参数。
默认窗口 1920x1200。页面简单或要省资源时再传 --width、--height；只传一边时另一边仍是默认值。
有头必须有 DISPLAY。不要用它去改或连接平台桌面 Chrome，也不要把密码写进参数或配置目录。
"""
from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_defaults import (  # noqa: E402
    PROFILE_DIR,
    command_uses_proxy,
    persistent_context_kwargs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="打开直连有头浏览器，默认 1920x1200，不走 8791")
    parser.add_argument("url", nargs="?", default="about:blank")
    parser.add_argument("--once", action="store_true", help="打开到 load 后立刻关闭，用来核对启动参数")
    parser.add_argument("--width", type=int, default=None, help="窗口宽度，默认 1920。页面简单或要省资源时再改小")
    parser.add_argument("--height", type=int, default=None, help="窗口高度，默认 1200。页面简单或要省资源时再改小")
    args = parser.parse_args()

    owner = os.environ.get("QA_OWNER", "")
    display = os.environ.get("DISPLAY", "")
    print(
        f"QA_OWNER={owner} DISPLAY={display} profile={PROFILE_DIR} url={args.url}",
        flush=True,
    )
    if not display:
        print("headed_need_display: 有头窗口需要 DISPLAY，例如 DISPLAY=:1", flush=True)
        return 2

    try:
        options = persistent_context_kwargs(width=args.width, height=args.height)
    except ValueError as exc:
        print(f"bad_window_size: {exc}", flush=True)
        return 2

    viewport = options["viewport"]
    print(
        f"viewport={viewport['width']}x{viewport['height']} headless={options['headless']} direct=1",
        flush=True,
    )
    if command_uses_proxy(options["args"]):
        print("unexpected_proxy_flag: 准备启动的参数里有代理，已取消", flush=True)
        return 3

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(**options)
        try:
            proc = context.browser.process if context.browser else None
            cmdline = []
            if proc is not None:
                try:
                    cmdline = proc.args or []
                except Exception:
                    cmdline = []
            uses_proxy = command_uses_proxy(cmdline)
            print("proxy_in_args", uses_proxy, flush=True)
            if uses_proxy:
                print("unexpected_proxy_flag: 启动参数里出现了代理，已关闭窗口", flush=True)
                return 3

            page = context.pages[0] if context.pages else context.new_page()
            start = time.time()
            try:
                page.goto(args.url, wait_until="load", timeout=30000)
                print(
                    "load_s",
                    round(time.time() - start, 2),
                    "final",
                    page.url,
                    "title",
                    page.title(),
                    flush=True,
                )
            except Exception as e:
                print("goto_fail", round(time.time() - start, 2), type(e).__name__, e, flush=True)
                if args.once:
                    return 1

            if args.once:
                return 0
            while True:
                time.sleep(60)
                if not context.browser or not context.browser.is_connected():
                    print("browser_closed", flush=True)
                    break
            return 0
        finally:
            context.close()


if __name__ == "__main__":
    raise SystemExit(main())
