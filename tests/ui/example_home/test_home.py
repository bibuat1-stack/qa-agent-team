"""示例 UI 用例：演示站点 playwright.dev 的首页，用来验证 Playwright 环境和流水线能跑通。

接入被测系统后删除本目录和 pages/example_home_page.py，按业务模块新建 tests/ui/<模块>/。
"""
from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect

from pages.example_home_page import ExampleHomePage

pytestmark = [pytest.mark.ui, pytest.mark.example_home]


class TestHomePage:
    """首页（示例）"""

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_home_page_loads(self, home_page: ExampleHomePage):
        """
        用例编号：UI-HOME-001
        用例名称：首页正常打开
        前置条件：UI 基础地址指向演示站点 https://playwright.dev
        测试步骤：1. 打开首页
        预期结果：页面标题包含 "Playwright"；"Get started" 链接可见
        """
        home_page.open()

        expect(home_page.page).to_have_title(re.compile("Playwright"))
        expect(home_page.get_started_link).to_be_visible()

    @pytest.mark.regression
    def test_get_started_opens_installation_doc(self, home_page: ExampleHomePage):
        """
        用例编号：UI-HOME-002
        用例名称：点击 Get started 进入安装文档
        前置条件：同 UI-HOME-001
        测试步骤：1. 打开首页；2. 点击 "Get started"
        预期结果：地址包含 /docs/intro；页面出现 "Installation" 标题
        """
        home_page.open()
        home_page.click_get_started()

        expect(home_page.page).to_have_url(re.compile(r"/docs/intro"))
        expect(home_page.heading("Installation")).to_be_visible()
