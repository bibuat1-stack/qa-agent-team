"""示例页面对象：Playwright 官网首页。演示目标，接入被测系统后替换为真实页面。"""
from __future__ import annotations

from playwright.sync_api import Locator

from pages.base_page import BasePage


class ExampleHomePage(BasePage):
    path = "/"

    @property
    def get_started_link(self) -> Locator:
        return self.page.get_by_role("link", name="Get started")

    def click_get_started(self) -> None:
        self.get_started_link.click()
