"""全局配置：环境变量优先，其次项目根目录的 .env，最后是默认值。令牌和密码只从环境变量读取。"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from config.environment import env_value, load_environment

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")  # 不覆盖已存在的环境变量（例如 CI 注入的）

_env = load_environment()


class Settings:
    ENVIRONMENT = _env.name
    BASE_URL = _env.api_base_url
    UI_BASE_URL = _env.ui_base_url

    API_TOKEN = env_value("API_TOKEN")
    UI_USERNAME = env_value("UI_USERNAME")
    UI_PASSWORD = env_value("UI_PASSWORD")

    TIMEOUT = float(env_value("TIMEOUT", "10"))
    RETRY_TIMES = int(env_value("RETRY_TIMES", "2"))
    LOG_LEVEL = env_value("LOG_LEVEL", "INFO").upper()

    DATA_DIR = _ROOT / "data"
    LOG_DIR = _ROOT / "logs"


settings = Settings()
