#!/usr/bin/env python3
"""在当前桌面打开直连有头 Chromium，使用固定配置目录，不走 8791。

用法：
  QA_OWNER=<号名> DISPLAY=:<显示号> python3 /workspace/qa/bin/open_direct_headed.py [网址]
  QA_OWNER=<号名> python3 /workspace/qa/bin/open_direct_headed.py --once [网址]

默认一直开着，关窗口或进程后退出。--once 只打开到 load 就关，用来核对启动参数。
不要用它去改或连接平台桌面 Chrome。
"""
from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from browser_defaults import PROFILE_DIR, persistent_context_kwargs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="打开直连有头浏览器")
    parser.add_argument("url", nargs="?", default="about:blank")
    parser.add_argument("--once", action="store_true", help="打开到 load 后立刻关闭")
    args = parser.parse_args()

    owner = os.environ.get("QA_OWNER", "")
    display = os.environ.get("DISPLAY", "")
    print(
        f"QA_OWNER={owner} DISPLAY={display} profile={PROFILE_DIR} url={args.url}",
        flush=True,
    )
    if not args.once and not display:
        print("headed_need_display: 有头窗口需要 DISPLAY，例如 DISPLAY=:1", flush=True)
        return 2

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(**persistent_context_kwargs())
        try:
            proc = context.browser.process if context.browser else None
            cmdline = []
            if proc is not None:
                try:
                    cmdline = proc.args or []
                except Exception:
                    cmdline = []
            proxy_in_args = any("proxy" in str(x).lower() for x in cmdline)
            print("proxy_in_args", proxy_in_args, flush=True)
            if proxy_in_args:
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
