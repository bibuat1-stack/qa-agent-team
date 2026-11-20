"""按固定顺序读取测号密码。仓库、日志和异常里不放密码。"""

from __future__ import annotations

import importlib.util
import os
import re
from pathlib import Path
from urllib.parse import quote

EXIT_MISSING_SECRET = 2

LOCAL_ACCOUNTS_PATH = Path("/workspace/qa/secrets/qa-test-accounts.md")
POINTER_PATH = Path("/workspace/qa/secrets/account-sheet-pointers.md")
PROJECT_MARK = "T8T"

_SPREADSHEET_IN_URL = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")
_BARE_ID = re.compile(r"^[a-zA-Z0-9-_]{20,}$")


class MissingSecret(Exception):
    """查找链上没有这个号的密码。"""


def missing_secret_message() -> str:
    return (
        "缺少密码，退出码 2。没有编造密码。\n"
        "查找顺序：\n"
        "1. 本机 /workspace/qa/secrets/qa-test-accounts.md（权限 600，不进仓库），"
        "或 T8T_ACCOUNTS_MODULE 的 get_password(phone)。\n"
        "2. 本机没有该号密码时，再查谷歌表「测试账号-完整库」里本项目的工作表。"
        "地址只从本机 /workspace/qa/secrets/account-sheet-pointers.md"
        "或环境变量 T8T_ACCOUNT_SHEET_POINTER 读取。没有谷歌凭证就跳过，不编造密码。\n"
        "3. 再看环境变量 T8T_SECRET_FILE，或 T8T_QA_TEMP_MIRROR 指向的本机「QA临时文件」镜像。\n"
        "4. 环境变量 T8T_PASSWORD 只作最后的临时覆盖，不是正式来源。\n"
        "「测试账号-给人看」和 Notion「测试账号」不是查找来源。"
    )


def load_password(phone: str) -> str:
    """返回密码。调用方不得打印返回值。"""
    for reader in (
        _from_local_file,
        _from_module_env,
        _from_sheet,
        _from_temp_files,
        _from_password_env,
    ):
        found = reader(phone)
        if found:
            return found
    raise MissingSecret(missing_secret_message())


def password_from_text(text: str, phone: str) -> str | None:
    """从账号表正文里取该号密码。跳过「测试账号-给人看」小节。"""
    rows: list[list[str]] = []
    skipping = False
    for line in text.splitlines():
        heading = line.strip()
        if heading.startswith("#"):
            skipping = "给人看" in heading
            continue
        if skipping or "给人看" in line:
            continue
        row = _split_row(line)
        if row:
            rows.append(row)
    return password_from_rows(rows, phone)


def password_from_rows(rows: list[list[str]], phone: str) -> str | None:
    header_at = None
    for index, row in enumerate(rows):
        if "账号" in row and "密码" in row:
            header_at = index
            break
    if header_at is None:
        return None
    header = rows[header_at]
    account_at = header.index("账号")
    password_at = header.index("密码")
    matches: list[list[str]] = []
    for row in rows[header_at + 1 :]:
        if max(account_at, password_at) >= len(row):
            continue
        if row[account_at].strip() != phone:
            continue
        if not row[password_at].strip():
            continue
        matches.append(row)
    if not matches:
        return None
    for row in matches:
        if PROJECT_MARK in "".join(row).upper():
            return row[password_at].strip()
    return matches[0][password_at].strip()


def _from_local_file(phone: str) -> str | None:
    return _password_in_file(LOCAL_ACCOUNTS_PATH, phone)


def _from_module_env(phone: str) -> str | None:
    module_path = os.environ.get("T8T_ACCOUNTS_MODULE", "").strip()
    if not module_path:
        return None
    return _from_module(module_path, phone)


def _from_module(module_path: str, phone: str) -> str | None:
    try:
        spec = importlib.util.spec_from_file_location("t8t_local_accounts", module_path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        getter = getattr(module, "get_password", None)
        if not callable(getter):
            return None
        value = getter(phone)
    except Exception:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _from_sheet(phone: str) -> str | None:
    spreadsheet_id = _spreadsheet_id()
    token = _google_token()
    if not spreadsheet_id or not token:
        return None
    try:
        title = _project_sheet_title(spreadsheet_id, token)
        if not title:
            return None
        rows = _sheet_rows(spreadsheet_id, token, title)
    except Exception:
        return None
    return password_from_rows(rows, phone)


def _from_temp_files(phone: str) -> str | None:
    for path in _temp_paths():
        found = _password_in_file(path, phone)
        if found:
            return found
    return None


def _from_password_env(phone: str) -> str | None:
    del phone
    value = os.environ.get("T8T_PASSWORD", "").strip()
    return value or None


def _password_in_file(path: Path, phone: str) -> str | None:
    if not path.is_file():
        return None
    if "给人看" in path.name:
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    return password_from_text(text, phone)


def _temp_paths() -> list[Path]:
    paths: list[Path] = []
    secret_file = os.environ.get("T8T_SECRET_FILE", "").strip()
    if secret_file:
        paths.append(Path(secret_file))
    mirror = os.environ.get("T8T_QA_TEMP_MIRROR", "").strip()
    if mirror:
        mirror_path = Path(mirror)
        if mirror_path.is_dir():
            paths.append(mirror_path / "qa-test-accounts.md")
        else:
            paths.append(mirror_path)
    return paths


def _spreadsheet_id() -> str | None:
    pointer = os.environ.get("T8T_ACCOUNT_SHEET_POINTER", "").strip()
    if pointer:
        pointer_path = Path(pointer)
        if pointer_path.is_file():
            return _id_from_pointer_text(_read_quiet(pointer_path))
        return _id_from_pointer_text(pointer)
    if POINTER_PATH.is_file():
        return _id_from_pointer_text(_read_quiet(POINTER_PATH))
    return None


def _id_from_pointer_text(text: str) -> str | None:
    for line in text.splitlines() or [text]:
        if "给人看" in line:
            continue
        match = _SPREADSHEET_IN_URL.search(line)
        if match and ("完整库" in line or "spreadsheets" in line):
            return match.group(1)
    for line in text.splitlines() or [text]:
        if "给人看" in line or "完整库" not in line:
            continue
        for token in re.split(r"\s+", line.strip()):
            if _BARE_ID.fullmatch(token):
                return token
    only = text.strip()
    match = _SPREADSHEET_IN_URL.search(only)
    if match and "给人看" not in only:
        return match.group(1)
    if _BARE_ID.fullmatch(only):
        return only
    return None


def _google_token() -> str | None:
    for key in ("T8T_GOOGLE_ACCESS_TOKEN", "GOOGLE_ACCESS_TOKEN"):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return None


def _project_sheet_title(spreadsheet_id: str, token: str) -> str | None:
    payload = _google_json(
        f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}"
        "?fields=sheets.properties.title",
        token,
    )
    titles = [
        sheet.get("properties", {}).get("title", "")
        for sheet in payload.get("sheets", [])
        if isinstance(sheet, dict)
    ]
    for title in titles:
        if "给人看" in title:
            continue
        if PROJECT_MARK.lower() in title.lower():
            return title
    return None


def _sheet_rows(spreadsheet_id: str, token: str, title: str) -> list[list[str]]:
    target = quote(f"'{title}'!A1:Z500", safe="")
    payload = _google_json(
        f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{target}",
        token,
    )
    rows = []
    for raw in payload.get("values", []):
        if isinstance(raw, list):
            rows.append([str(cell) for cell in raw])
    return rows


def _google_json(url: str, token: str) -> dict:
    import json
    from urllib.request import Request, urlopen

    request = Request(url, headers={"Authorization": f"Bearer {token}"})
    with urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        return {}
    return payload


def _read_quiet(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _split_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if "|" in stripped:
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(set(cell) <= set("-: ") and cell for cell in cells):
            return None
        return cells
    if "\t" in stripped:
        return [cell.strip() for cell in stripped.split("\t")]
    return None
