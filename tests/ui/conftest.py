"""UI 用例的 fixture：被测地址、页面对象和登录账号。浏览器相关 fixture（page 等）来自 pytest-playwright。"""
from __future__ import annotations

import os

import pytest
from playwright.sync_api import Page

from config.settings import settings
from pages.example_home_page import ExampleHomePage


def _cloud_computer() -> bool:
    return os.environ.get("QA_CLOUD") == "1"


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    """云电脑上关掉 GPU 和 /dev/shm 依赖，减少小内存机器上的浏览器崩溃。本地和 CI 不改启动参数。"""
    if not _cloud_computer():
        return browser_type_launch_args
    args = list(browser_type_launch_args.get("args", []))
    for flag in ("--disable-dev-shm-usage", "--disable-gpu"):
        if flag not in args:
            args.append(flag)
    return {**browser_type_launch_args, "args": args}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """云电脑用较小视口并减少动画，降低截图体积和绘制开销。"""
    if not _cloud_computer():
        return browser_context_args
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}, "reduced_motion": "reduce"}


@pytest.fixture(scope="session")
def base_url(pytestconfig: pytest.Config) -> str:
    """覆盖 pytest-base-url 的同名 fixture：命令行 --base-url 优先，否则用 UI_BASE_URL / 当前环境的 UI 地址。"""
    return pytestconfig.getoption("base_url") or settings.UI_BASE_URL


@pytest.fixture
def ui_credentials() -> dict[str, str]:
    """需要登录的用例使用；没有配置 UI_USERNAME / UI_PASSWORD 时跳过，不会把空账号发出去。"""
    if not (settings.UI_USERNAME and settings.UI_PASSWORD):
        pytest.skip("未设置 UI_USERNAME / UI_PASSWORD")
    return {"username": settings.UI_USERNAME, "password": settings.UI_PASSWORD}


@pytest.fixture
def home_page(page: Page, base_url: str) -> ExampleHomePage:
    return ExampleHomePage(page, base_url)
