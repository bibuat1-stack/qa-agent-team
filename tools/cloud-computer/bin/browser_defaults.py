#!/usr/bin/env python3
"""直连浏览器的共用启动参数。页面测试默认无头、不走 8791。

有头窗口只用在用户要盯着看或接手时。UI 回归默认无头；有头窗口和固定视口
默认 1920x1200。页面简单或要省资源时，再传入更小的 width、height。

配置目录只给有头直连窗口用，和平台桌面 Chrome 分开。
不要改平台 Chrome 的策略、启动参数或代理。不要把密码写进参数或配置目录。

用法：
    browser = chromium.launch(**launch_kwargs())          # 默认无头、直连
    context = browser.new_context(**context_kwargs())     # 默认 1920x1200
    # 页面简单或要省资源：
    context = browser.new_context(**context_kwargs(width=1280, height=800))
    # 有头直连窗口（配置目录 ~/.config/chrome-direct）：
    context = chromium.launch_persistent_context(**persistent_context_kwargs())
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

PROFILE_DIR = Path(os.environ.get("QA_CHROME_DIRECT_PROFILE", os.path.expanduser("~/.config/chrome-direct")))
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1200
VIEWPORT = {"width": WINDOW_WIDTH, "height": WINDOW_HEIGHT}
LOCALE = "zh-CN"
TIMEZONE_ID = "Asia/Shanghai"

# 窗口尺寸放第一项，方便肉眼核对。改尺寸用 launch_args(width=, height=)，
# 不要按下标改这一项。/dev/shm 现约 8GiB，不必再禁用。
LAUNCH_ARGS = [
    f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}",
    "--window-position=0,0",
    "--no-sandbox",
    "--no-first-run",
    "--no-default-browser-check",
    "--no-proxy-server",
    "--disable-background-networking",
    "--disable-sync",
    "--disable-features=Translate,MediaRouter",
    "--password-store=basic",
]

# 不含 viewport。viewport 每次按请求现做，避免和 VIEWPORT 共用同一个字典。
_CONTEXT_BASE = {
    "reduced_motion": "reduce",
    "locale": LOCALE,
    "timezone_id": TIMEZONE_ID,
    "ignore_https_errors": False,
}

CONTEXT_KWARGS = {**_CONTEXT_BASE, "viewport": dict(VIEWPORT)}

# 这些才是「走代理」。--no-proxy-server 是直连，不能拿「参数里有没有 proxy」来判断。
_PROXY_SERVER_FLAGS = ("--proxy-server", "--proxy-pac-url")


def ensure_profile() -> Path:
    """创建有头直连窗口的配置目录。无头回归和平台 Chrome 都不要用这份目录。"""
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    return PROFILE_DIR


def _size(width: Optional[int], height: Optional[int]) -> tuple[int, int]:
    """缺省 1920x1200。传入的宽高必须是正整数，0 不会再被当成「没传」。"""
    w = WINDOW_WIDTH if width is None else width
    h = WINDOW_HEIGHT if height is None else height
    for name, value in (("width", w), ("height", h)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} 必须是正整数，收到 {value!r}")
    return w, h


def viewport_for(width: Optional[int] = None, height: Optional[int] = None) -> dict:
    """默认 1920x1200。页面简单或要省资源时传入更小的宽高。只传一边时，另一边仍用默认。"""
    w, h = _size(width, height)
    return {"width": w, "height": h}


def command_uses_proxy(args: list[str]) -> bool:
    """启动参数里是否指定了代理服务器。--no-proxy-server 返回 False。"""
    for raw in args:
        item = str(raw).strip().lower()
        for flag in _PROXY_SERVER_FLAGS:
            if item == flag or item.startswith(flag + "="):
                return True
    return False


def launch_args(*, width: Optional[int] = None, height: Optional[int] = None) -> list[str]:
    """返回一份新的 Chromium 启动参数。不修改 LAUNCH_ARGS。

    默认和 LAUNCH_ARGS 相同。传入 width、height 时只换 --window-size，
    其余参数保持原顺序。
    """
    w, h = _size(width, height)
    size_flag = f"--window-size={w},{h}"
    args = [size_flag]
    for item in LAUNCH_ARGS:
        if str(item).startswith("--window-size="):
            continue
        args.append(item)
    return args


def launch_kwargs(*, headless: bool = True, width: Optional[int] = None, height: Optional[int] = None) -> dict:
    """给 playwright.chromium.launch 用。

    UI 回归默认无头。proxy 固定为 None，不走 8791。
    无头不要把 user_data_dir 指到 PROFILE_DIR；有头直连窗口用 persistent_context_kwargs()。
    """
    return {
        "headless": headless,
        "proxy": None,
        "args": launch_args(width=width, height=height),
    }


def context_kwargs(*, width: Optional[int] = None, height: Optional[int] = None) -> dict:
    """给 browser.new_context 用。每次返回新字典，默认视口 1920x1200。

    改 CONTEXT_KWARGS 不会影响之后的调用。要改这次的视口，传入 width、height。
    """
    return {**_CONTEXT_BASE, "viewport": viewport_for(width, height)}


def persistent_context_kwargs(*, headless: bool = False, width: Optional[int] = None, height: Optional[int] = None) -> dict:
    """给 chromium.launch_persistent_context 用，只用于有头直连窗口。

    默认有头，配置目录是 PROFILE_DIR（默认 ~/.config/chrome-direct）。
    headless 参数仍可传入，无头回归不要改走这个函数。
    """
    kwargs = context_kwargs(width=width, height=height)
    kwargs.update(
        user_data_dir=str(ensure_profile()),
        headless=headless,
        proxy=None,
        args=launch_args(width=width, height=height),
    )
    return kwargs
