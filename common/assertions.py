"""通用断言：失败信息带上字段路径、期望值、实际值和响应摘要，便于直接定位问题。

source 参数可以传 requests.Response（自动取 JSON）或已经解析好的值。
字段路径用点号分隔，列表下标写数字：data.items.0.id，也可以写成 data.items[0].id。
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import requests

from common.utils import redact_text, response_text, to_log_text, truncate


def _summary(response: requests.Response) -> str:
    return (
        f"请求：{response.request.method} {redact_text(response.url)}\n"
        f"响应：{response.status_code} {truncate(response_text(response), 1000)}"
    )


def _json(source: Any) -> Any:
    if not isinstance(source, requests.Response):
        return source
    try:
        return source.json()
    except ValueError:
        raise AssertionError(f"响应体不是合法 JSON\n{_summary(source)}") from None


def _show(value: Any) -> str:
    return truncate(to_log_text(value) if isinstance(value, (dict, list)) else redact_text(repr(value)), 500)


def _is_empty(value: Any) -> bool:
    return value is None or (hasattr(value, "__len__") and len(value) == 0)


def get_field(source: Any, path: str) -> Any:
    """按路径取字段，路径为空时返回整个 JSON。字段不存在时断言失败。"""
    data = _json(source)
    current = data
    for key in [part for part in re.sub(r"\[(\d+)\]", r".\1", path).split(".") if part]:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and key.isdigit() and int(key) < len(current):
            current = current[int(key)]
        else:
            raise AssertionError(f"字段不存在：{path}（找不到 {key!r}）\n实际数据：{_show(data)}")
    return current


def assert_status_code(response: requests.Response, expected: int | Iterable[int]) -> None:
    allowed = [expected] if isinstance(expected, int) else list(expected)
    if response.status_code not in allowed:
        raise AssertionError(f"状态码不符：期望 {expected}，实际 {response.status_code}\n{_summary(response)}")


def assert_json_field(source: Any, path: str, expected: Any) -> None:
    actual = get_field(source, path)
    if actual != expected:
        raise AssertionError(f"字段 {path} 不符：期望 {expected!r}，实际 {_show(actual)}")


def assert_contains(container: Any, member: Any, desc: str = "实际值") -> None:
    """字符串判断子串，列表判断元素，字典判断键。"""
    container = _json(container)
    if container is None or member not in container:
        raise AssertionError(f"{desc} 应包含 {member!r}，实际：{_show(container)}")


def assert_not_contains(container: Any, member: Any, desc: str = "实际值") -> None:
    container = _json(container)
    if container is not None and member in container:
        raise AssertionError(f"{desc} 不应包含 {member!r}，实际：{_show(container)}")


def assert_json_contains(source: Any, path: str, member: Any) -> None:
    assert_contains(get_field(source, path), member, desc=f"字段 {path}")


def assert_json_not_contains(source: Any, path: str, member: Any) -> None:
    assert_not_contains(get_field(source, path), member, desc=f"字段 {path}")


def assert_is_list(value: Any, desc: str = "实际值") -> None:
    value = _json(value)
    if not isinstance(value, list):
        raise AssertionError(f"{desc} 应为列表，实际类型 {type(value).__name__}：{_show(value)}")


def assert_list_length(value: Any, expected: int, desc: str = "列表") -> None:
    value = _json(value)
    assert_is_list(value, desc)
    if len(value) != expected:
        raise AssertionError(f"{desc} 长度不符：期望 {expected}，实际 {len(value)}")


def assert_each_item_field(items: Any, path: str, expected: Any, desc: str = "列表") -> None:
    """列表中每个元素的 path 字段都等于 expected，例如筛选接口的结果校验。"""
    items = _json(items)
    assert_is_list(items, desc)
    wrong = [(index, value) for index, value in enumerate(get_field(item, path) for item in items) if value != expected]
    if wrong:
        raise AssertionError(
            f"{desc} 中有 {len(wrong)} 个元素的 {path} 不等于 {expected!r}，前 5 个（下标, 实际值）：{wrong[:5]}"
        )


def assert_empty(value: Any, desc: str = "实际值") -> None:
    value = _json(value)
    if not _is_empty(value):
        raise AssertionError(f"{desc} 应为空，实际：{_show(value)}")


def assert_not_empty(value: Any, desc: str = "实际值") -> None:
    value = _json(value)
    if _is_empty(value):
        raise AssertionError(f"{desc} 不应为空，实际：{value!r}")
