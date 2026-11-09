"""多环境（dev/test/pre/prod）地址表与切换。

当前环境由 ENVIRONMENT 决定，默认 test（CI 中来自仓库变量 TEST_ENV）。
环境变量 BASE_URL / UI_BASE_URL 会覆盖表中的地址，适合 CI 和临时调试。
"""
from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_ENVIRONMENT = "test"

# 示例目标：公共演示站点，只为让示例用例开箱即跑。接入被测系统时替换为各环境的真实地址。
ENVIRONMENTS: dict[str, dict[str, str]] = {
    "dev": {
        "api_base_url": "https://jsonplaceholder.typicode.com",
        "ui_base_url": "https://playwright.dev",
    },
    "test": {
        "api_base_url": "https://jsonplaceholder.typicode.com",
        "ui_base_url": "https://playwright.dev",
    },
    "pre": {
        "api_base_url": "https://jsonplaceholder.typicode.com",
        "ui_base_url": "https://playwright.dev",
    },
    "prod": {
        "api_base_url": "https://jsonplaceholder.typicode.com",
        "ui_base_url": "https://playwright.dev",
    },
}


@dataclass(frozen=True)
class Environment:
    name: str
    api_base_url: str
    ui_base_url: str


def env_value(name: str, default: str = "") -> str:
    # GitHub Actions 会把未设置的仓库变量传成空字符串，这里按未设置处理。
    return os.getenv(name, "").strip() or default


def load_environment() -> Environment:
    name = env_value("ENVIRONMENT", DEFAULT_ENVIRONMENT).lower()
    if name not in ENVIRONMENTS:
        raise ValueError(f"未知环境 ENVIRONMENT={name!r}，可选：{'/'.join(ENVIRONMENTS)}")
    urls = ENVIRONMENTS[name]
    return Environment(
        name=name,
        api_base_url=env_value("BASE_URL", urls["api_base_url"]).rstrip("/"),
        ui_base_url=env_value("UI_BASE_URL", urls["ui_base_url"]).rstrip("/"),
    )
