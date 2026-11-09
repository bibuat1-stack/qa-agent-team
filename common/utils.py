"""通用工具：时间戳、随机数据、摘要、测试数据读取，以及日志和断言信息用的脱敏。"""
from __future__ import annotations

import hashlib
import json
import random
import re
import string
from collections.abc import Mapping
from datetime import datetime
from typing import Any

import yaml

from config.settings import settings

MASK = "***"
_SENSITIVE_KEY = re.compile(r"authorization|cookie|password|passwd|pwd|secret|token|api[-_]?key|session", re.I)
_AUTH_SCHEME = re.compile(r"\b(bearer|basic)\s+[\w.~+/=-]+", re.I)
_JWT = re.compile(r"\beyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]{10,}")
# 键名命中敏感词时只替换值。(?<![\w-]) 让匹配只从单词开头尝试，避免长文本上的回溯。
# 两种写法分开扫描：否则 "https://host?token=x" 会被当成键 https 整段吞掉，token 漏掉。
_EQUALS_PAIR = re.compile(r"(?<![\w-])([\w-]+)(\s*=\s*)([^&\s#]*)")
_COLON_PAIR = re.compile(r"(?<![\w-])([\"']?)([\w-]+)\1(\s*:\s*)(\"(?:[^\"\\]|\\.)*\"|'[^']*'|[^\s,;}\]]+)")


def timestamp(fmt: str = "%Y%m%d%H%M%S") -> str:
    return datetime.now().strftime(fmt)


def random_string(length: int = 8, chars: str = string.ascii_lowercase + string.digits) -> str:
    return "".join(random.choices(chars, k=length))


def unique_name(prefix: str = "auto") -> str:
    """带时间戳和随机后缀的名称，避免测试数据互相冲突。"""
    return f"{prefix}_{timestamp()}_{random_string(4)}"


def md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def load_data(relative_path: str) -> Any:
    """读取 data/ 下的 YAML 或 JSON 文件，例如 load_data("test_cases/example_posts.yaml")。"""
    path = settings.DATA_DIR / relative_path
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    if path.suffix == ".json":
        return json.loads(text)
    raise ValueError(f"不支持的数据文件类型：{path}")


def truncate(text: str, limit: int = 2000) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]}…（共 {len(text)} 字符，已截断）"


def redact_headers(headers: Mapping[str, Any]) -> dict[str, str]:
    return {key: MASK if _SENSITIVE_KEY.search(key) else redact_text(str(value)) for key, value in headers.items()}


def redact_data(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: MASK if isinstance(key, str) and _SENSITIVE_KEY.search(key) else redact_data(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact_data(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def redact_text(text: str) -> str:
    text = _AUTH_SCHEME.sub(rf"\1 {MASK}", text)
    text = _JWT.sub(MASK, text)
    text = _EQUALS_PAIR.sub(lambda m: f"{m[1]}{m[2]}{MASK}" if _SENSITIVE_KEY.search(m[1]) else m[0], text)
    return _COLON_PAIR.sub(lambda m: f"{m[1]}{m[2]}{m[1]}{m[3]}{MASK}" if _SENSITIVE_KEY.search(m[2]) else m[0], text)


def to_log_text(value: Any) -> str:
    """把请求或响应内容转成脱敏后的文本。"""
    if isinstance(value, (Mapping, list, tuple)):
        return json.dumps(redact_data(value), ensure_ascii=False, default=str)
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return redact_text(str(value))


def response_text(response: Any) -> str:
    """响应体的脱敏文本：JSON 按字段脱敏，其他内容按文本规则脱敏。"""
    try:
        return to_log_text(response.json())
    except ValueError:
        return redact_text(response.text)
