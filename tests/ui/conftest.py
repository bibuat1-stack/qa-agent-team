"""UI 用例的 fixture：被测地址、页面对象和登录账号。浏览器相关 fixture（page 等）来自 pytest-playwright。"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from config.settings import settings
from pages.example_home_page import ExampleHomePage


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
