"""Page Object 基类：页面对象只放定位器和页面操作，断言写在用例里（用 Playwright 的 expect）。"""
from __future__ import annotations

from playwright.sync_api import Locator, Page


class BasePage:
    path = "/"  # 相对 UI 基础地址的路径，子类覆盖

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    @property
    def url(self) -> str:
        return f"{self.base_url}/{self.path.lstrip('/')}"

    def open(self) -> None:
        self.page.goto(self.url)

    def heading(self, name: str) -> Locator:
        return self.page.get_by_role("heading", name=name)
