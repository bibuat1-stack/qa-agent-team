#!/usr/bin/env python3
"""直连浏览器的共用启动参数。页面测试默认无头、不走 8791。

有头窗口只用在用户要盯着看或接手时。UI 回归无论无头还是有头，默认用大视口
1920x1200（有头窗口同样 1920x1200），减少动画，方便看清页面。软件渲染按像素
耗 CPU，但实测瓶颈在代理不在渲染，影响不大时就用大窗口。页面简单、或明确要
省资源时，再传入更小的 width、height。

配置目录只给有头直连窗口用，和平台桌面 Chrome 分开。
不要改平台 Chrome 的策略、启动参数或代理。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

PROFILE_DIR = Path(os.environ.get("QA_CHROME_DIRECT_PROFILE", os.path.expanduser("~/.config/chrome-direct")))
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1200
VIEWPORT = {"width": 1920, "height": 1200}
LOCALE = "zh-CN"
TIMEZONE_ID = "Asia/Shanghai"

# /dev/shm 现约 8GiB，不必再禁用。
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

CONTEXT_KWARGS = {
    "viewport": VIEWPORT,
    "reduced_motion": "reduce",
    "locale": LOCALE,
    "timezone_id": TIMEZONE_ID,
    "ignore_https_errors": False,
}


def ensure_profile() -> Path:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    return PROFILE_DIR


def viewport_for(width: Optional[int] = None, height: Optional[int] = None) -> dict:
    """默认大视口；要改小时传入实际宽高。"""
    return {
        "width": width or VIEWPORT["width"],
        "height": height or VIEWPORT["height"],
    }


def launch_args(*, width: Optional[int] = None, height: Optional[int] = None) -> list[str]:
    w = width or WINDOW_WIDTH
    h = height or WINDOW_HEIGHT
    args = list(LAUNCH_ARGS)
    args[0] = f"--window-size={w},{h}"
    return args


def launch_kwargs(*, headless: bool = True, width: Optional[int] = None, height: Optional[int] = None) -> dict:
    """给 playwright.chromium.launch 用。UI 回归默认无头；无头不要复用有头配置目录。"""
    return {
        "headless": headless,
        "proxy": None,
        "args": launch_args(width=width, height=height),
    }


def context_kwargs(*, width: Optional[int] = None, height: Optional[int] = None) -> dict:
    """给 browser.new_context 用。默认大视口，要省资源再改小。"""
    kwargs = dict(CONTEXT_KWARGS)
    kwargs["viewport"] = viewport_for(width, height)
    return kwargs


def persistent_context_kwargs(*, headless: bool = False, width: Optional[int] = None, height: Optional[int] = None) -> dict:
    """给 chromium.launch_persistent_context 用，只用于有头直连窗口。"""
    return {
        "user_data_dir": str(ensure_profile()),
        "headless": headless,
        "proxy": None,
        "args": launch_args(width=width, height=height),
        **context_kwargs(width=width, height=height),
    }
