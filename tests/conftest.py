"""全局 fixture 与钩子：报告里写明当前环境、读取请求数据、结束时关闭 HTTP 会话。"""
from __future__ import annotations

import platform
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

from common.http_client import http_client
from common.utils import load_data
from config.settings import settings


def _environment_info() -> dict[str, str]:
    return {
        "ENVIRONMENT": settings.ENVIRONMENT,
        "BASE_URL": settings.BASE_URL,
        "UI_BASE_URL": settings.UI_BASE_URL,
        "Python": platform.python_version(),
    }


def pytest_report_header() -> str:
    return "  ".join(f"{key}={value}" for key, value in _environment_info().items())


def pytest_sessionfinish(session: pytest.Session) -> None:
    # 写入 Allure 报告的 Environment 面板，分诊时可以直接看到这次跑的是哪个环境。
    alluredir = getattr(session.config.option, "allure_report_dir", None)
    if alluredir and Path(alluredir).is_dir():
        lines = [f"{key}={value}" for key, value in _environment_info().items()]
        (Path(alluredir) / "environment.properties").write_text("\n".join(lines) + "\n", encoding="utf-8")


@pytest.fixture(scope="session", autouse=True)
def _close_http_client() -> Iterator[None]:
    yield
    http_client.close()


@pytest.fixture
def api_data() -> Callable[[str], Any]:
    """读取 data/api_data/ 下的请求数据；每次调用都重新读取，用例可以放心修改返回值。"""
    return lambda name: load_data(f"api_data/{name}")
