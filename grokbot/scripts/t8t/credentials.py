"""读取测号密码。仓库和日志里不放密码。"""

from __future__ import annotations

import importlib.util
import os

EXIT_MISSING_SECRET = 2


class MissingSecret(Exception):
    """本机没有可用的密码来源。"""


def missing_secret_message() -> str:
    return (
        "缺少密码，退出码 2。没有编造密码，也没有把密码写进仓库。\n"
        "任选一种再跑：\n"
        "1. 环境变量 T8T_PASSWORD\n"
        "2. 环境变量 T8T_ACCOUNTS_MODULE 指向本机 Python 模块，模块提供 get_password(phone)\n"
        "密码放在哪，读 grokbot/HANDOFF.md 的「测试账号在哪」。\n"
        "本机若已有探路账号模块，只在本机引用，不要把那个文件提交进仓库。\n"
        "常见位置是 /workspace/qa/t8t/multisite/thai-gray/lib/ 下的 accounts。"
    )


def load_password(phone: str) -> str:
    """返回密码字符串。调用方不得打印返回值。"""
    from_env = os.environ.get("T8T_PASSWORD", "").strip()
    if from_env:
        return from_env
    module_path = os.environ.get("T8T_ACCOUNTS_MODULE", "").strip()
    if module_path:
        password = _from_module(module_path, phone)
        if password:
            return password
    raise MissingSecret(missing_secret_message())


def _from_module(module_path: str, phone: str) -> str:
    spec = importlib.util.spec_from_file_location("t8t_local_accounts", module_path)
    if spec is None or spec.loader is None:
        raise MissingSecret(missing_secret_message())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    getter = getattr(module, "get_password", None)
    if not callable(getter):
        raise MissingSecret(
            missing_secret_message() + "\n本机模块没有 get_password(phone)。"
        )
    value = getter(phone)
    if not isinstance(value, str) or not value.strip():
        raise MissingSecret(missing_secret_message())
    return value.strip()
