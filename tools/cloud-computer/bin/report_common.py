#!/usr/bin/env python3
"""收工报告与缺陷文档的共用解析、脱敏和排版。"""
from __future__ import annotations

import html
import json
import re
import struct
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

SHANGHAI = timezone(timedelta(hours=8), name="Asia/Shanghai")
MISSING = "缺，待补"

RESULT_ORDER = ("失败", "阻塞", "通过", "未测", "未验证", "已跑待评审", "已跑待确认")
RESULT_NORMALIZE = {
    "pass": "通过",
    "passed": "通过",
    "ok": "通过",
    "success": "通过",
    "fail": "失败",
    "failed": "失败",
    "failure": "失败",
    "bug": "失败",
    "defect": "失败",
    "block": "阻塞",
    "blocked": "阻塞",
    "blocked_by_env": "阻塞",
    "skip": "未测",
    "skipped": "未测",
    "untested": "未测",
    "not_run": "未测",
    "unverified": "未验证",
    "pending": "已跑待确认",
    "need_confirm": "已跑待确认",
    "need_review": "已跑待评审",
}
# 「确认」计为通过；不可把「已跑待确认」「部分确认」算进来。
PASS_ALIASES = {"确认", "confirmed"}
NOT_PASS_ALIASES = {"已跑待确认", "部分确认", "待确认"}
FAIL_RESULTS = {"失败"}
BUG_MARK_KEYS = ("is_bug", "defect", "是缺陷", "bug", "列为缺陷")
REQ_POINT_KEYS = ("requirement_point", "req_point", "是需求点", "需求点", "in_requirement")
REQ_MISMATCH_KEYS = ("requirement_mismatch", "req_mismatch", "与需求不符", "不符需求")
TRUTHY = {"1", "true", "yes", "y", "是", "真", "ok", "on"}
FALSY = {"0", "false", "no", "n", "否", "假", "off"}
KNOWN_RESULT_STYLES = set(RESULT_ORDER) | {"未填", "部分确认", "确认"}

IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}
SECRET_TEXT = (
    (re.compile(r"(?i)\b(bearer)\s+\S+"), r"\1 ***"),
    (
        re.compile(r"(?i)\b(password|passwd|pwd|token|secret|cookie|authorization|otp)\b\s*[:=]\s*\S+"),
        r"\1=***",
    ),
    (re.compile(r"(验证码|密码|口令)\s*[:=：]\s*\S+"), r"\1=***"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"), "***"),
)
BLOCKED_PARTS = {"secrets", "leases"}

META_KIND = {"meta", "batch", "report", "批次", "报告", "元数据"}
PROJECT_KEYS = ("project", "项目", "project_name", "项目名")
BATCH_KEYS = ("batch", "批次", "batch_name", "批次名")
SLUG_KEYS = ("slug", "简称", "short_name", "name_key", "需求简称")
ENV_KEYS = ("environment", "env", "环境", "site", "站点")
SIDE_KEYS = ("side", "前后台", "client", "area", "端")
MACHINE_KEYS = ("machine", "机器", "machine_id", "host", "主机")
TIME_KEYS = ("time", "测试时间", "timestamp", "started_at", "start", "when")
ZONE_KEYS = ("timezone", "tz", "时区")
CONCLUSION_KEYS = ("conclusion", "结论", "one_liner", "人口结论", "summary_conclusion")
ID_KEYS = ("id", "编号", "case_id")
TITLE_KEYS = ("title", "名称", "name")
RESULT_KEYS = ("result", "结果", "status")
SUMMARY_KEYS = ("summary", "note", "说明", "caption", "描述")
PRE_KEYS = ("preconditions", "precondition", "前置条件", "前置")
STEP_KEYS = ("steps", "repro_steps", "repro", "复现步骤", "步骤")
EXPECTED_KEYS = ("expected", "expected_result", "预期结果", "预期")
ACTUAL_KEYS = ("actual", "actual_result", "实际结果", "实际")
BASIS_KEYS = ("basis", "依据", "source", "expected_basis", "预期依据")
SEVERITY_KEYS = ("severity", "严重程度", "level", "priority", "优先级")
IMPACT_KEYS = ("impact", "影响", "影响范围")

SHARED_CSS = """
:root {
  --bg: #f4f1ea;
  --card: #fffdf8;
  --ink: #1e1c18;
  --muted: #5e584e;
  --line: #e4ddd0;
  --navy: #24344a;
  --fail: #9b1c1c;
  --fail-bg: #fdecec;
  --block: #8a4b08;
  --block-bg: #fff4e5;
  --pass: #17663a;
  --pass-bg: #e8f6ee;
  --wait: #5b4aa8;
  --wait-bg: #f3f0fb;
  --skip: #4b5563;
  --skip-bg: #eef0f3;
  --miss: #8a4b08;
  --miss-bg: #fff7e8;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 16px/1.65 "Source Han Sans SC", "Noto Sans CJK SC", "Noto Sans SC",
        "PingFang SC", "Microsoft YaHei UI", "Microsoft YaHei", "Heiti SC",
        "Hiragino Sans GB", sans-serif;
}
.page { max-width: 1080px; margin: 0 auto; padding: 32px 28px 72px; }
h1, h2, h3 { line-height: 1.35; font-weight: 650; color: var(--navy); }
h1 { font-size: 28px; margin: 0 0 8px; }
h2 { font-size: 20px; margin: 36px 0 12px; padding-bottom: 6px; border-bottom: 1px solid var(--line); }
h3 { font-size: 18px; margin: 0 0 8px; color: var(--ink); }
p { margin: 0 0 8px; }
a { color: #1f4b7a; }
a:hover { color: #12314f; }
.banner {
  background: #fff7e8;
  border: 1px solid #e8d3a3;
  color: #6a4b10;
  padding: 10px 14px;
  border-radius: 8px;
  margin: 0 0 20px;
}
.meta { color: var(--muted); margin: 0 0 6px; }
.conclusion {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 16px 18px;
  margin: 18px 0;
}
.conclusion strong { color: var(--navy); }
.badges { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 4px; }
.badge, .tag {
  display: inline-block;
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 13px;
  font-weight: 650;
  line-height: 1.6;
  white-space: nowrap;
}
.badge-失败, .tag-失败 { color: var(--fail); background: var(--fail-bg); }
.badge-阻塞, .tag-阻塞 { color: var(--block); background: var(--block-bg); }
.badge-通过, .tag-通过 { color: var(--pass); background: var(--pass-bg); }
.badge-未测, .tag-未测, .badge-未验证, .tag-未验证 { color: var(--skip); background: var(--skip-bg); }
.badge-已跑待评审, .tag-已跑待评审,
.badge-已跑待确认, .tag-已跑待确认 { color: var(--wait); background: var(--wait-bg); }
.badge-其他, .tag-其他, .badge-未填, .tag-未填,
.badge-部分确认, .tag-部分确认 { color: var(--wait); background: var(--wait-bg); }
.tag-需求点 { color: #1f4b7a; background: #e8eef6; }
.tag-与需求不符 { color: var(--fail); background: var(--fail-bg); font-weight: 700; }
.tag-原结果 { color: var(--muted); background: var(--skip-bg); font-weight: 500; }
.case.mismatch, .bug.mismatch { border-left: 4px solid var(--fail); }
.reqbox {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 16px 18px;
  margin: 12px 0;
}
.reqbox.warn { border-left: 4px solid var(--block); background: var(--miss-bg); }
.reqbox ul { margin: 8px 0 0; padding-left: 22px; }
.toc, .filters, .case, .bug, .notes {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 16px 18px;
  margin: 12px 0;
}
.toc ol { margin: 0; padding-left: 22px; }
.toc li { margin: 4px 0; }
.filters[hidden] { display: none !important; }
.filters { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.filters button {
  font: inherit;
  cursor: pointer;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 4px 12px;
  color: var(--navy);
}
.filters button[aria-pressed="true"] { background: var(--navy); color: #fff; border-color: var(--navy); }
.case[hidden], .group[hidden] { display: none !important; }
.case-head { display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: baseline; margin-bottom: 8px; }
.case-head h3 { flex: 1 1 16em; }
.prose p { margin: 0 0 6px; }
.shot {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-start;
  margin: 14px 0 4px;
}
.shot-frame {
  position: relative;
  width: 100%;
}
button.shot-frame,
button.shot-open-area {
  font: inherit;
  background: none;
  border: 0;
  padding: 0;
  cursor: zoom-in;
  text-align: left;
  text-decoration: none;
  color: inherit;
}
.shot-sizer { width: 100%; }
.shot-frame img {
  display: block;
  width: 100%;
  height: auto;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fff;
}
.shot-box {
  position: absolute;
  border: 3px solid #c62828;
  box-sizing: border-box;
  pointer-events: none;
}
figcaption, .shot-cap { margin: 0; max-width: 36em; color: var(--muted); }
.shot-open {
  font: inherit;
  cursor: pointer;
  background: none;
  border: 0;
  color: #1f4b7a;
  padding: 0;
  text-decoration: underline;
}
.dl { display: grid; grid-template-columns: 8em 1fr; gap: 10px 16px; margin: 12px 0 0; }
.dl dt { color: var(--muted); font-weight: 650; padding-top: 2px; }
.dl dd { margin: 0; }
.ol-steps { margin: 0; padding-left: 22px; }
.ol-steps li { margin: 4px 0; }
.miss { background: var(--miss-bg); color: var(--miss); padding: 0 6px; border-radius: 4px; }
.linkbox { margin: 16px 0; padding: 12px 16px; border-left: 4px solid var(--fail); background: var(--fail-bg); }
.footer { color: var(--muted); font-size: 13px; margin-top: 36px; }
dialog { border: 1px solid var(--line); border-radius: 10px; padding: 16px; max-width: 96vw; background: #fff; }
dialog img { max-width: 92vw; max-height: 82vh; display: block; }
dialog::backdrop { background: rgba(20, 18, 14, .55); }
.dialog-bar { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 8px; }
@media print {
  body { background: #fff; }
  .filters, .shot-open, .dialog-bar { display: none !important; }
  .page { padding: 0; max-width: none; }
  .case, .bug, .toc, .conclusion { break-inside: avoid; }
}
""".strip()


def redact_text(value: str) -> str:
    for pattern, repl in SECRET_TEXT:
        value = pattern.sub(repl, value)
    return value


def first_raw(row: dict, keys: tuple[str, ...], default=None):
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return default


def first_text(row: dict, keys: tuple[str, ...], default: str = "") -> str:
    raw = first_raw(row, keys)
    if raw is None:
        return default
    if isinstance(raw, (list, tuple)):
        parts = [redact_text(str(item).strip()) for item in raw if item not in (None, "")]
        return "\n".join(parts) if parts else default
    return redact_text(str(raw))


def truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    if value in (None, "", 0):
        return False
    return str(value).strip().lower() in TRUTHY


def forbidden(path: Path) -> bool:
    try:
        parts = {part.lower() for part in path.resolve().parts}
    except OSError:
        return True
    return bool(BLOCKED_PARTS.intersection(parts))


def inside(path: Path, root: Path) -> bool:
    try:
        resolved = path.resolve()
        resolved.relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return resolved.is_file() and not forbidden(resolved)


def parse_box(value) -> tuple[int, int, int, int] | None:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None
    numbers = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            return None
        if item < 0:
            return None
        numbers.append(int(item))
    if numbers[2] <= 0 or numbers[3] <= 0:
        return None
    return numbers[0], numbers[1], numbers[2], numbers[3]


def shot_list(row: dict) -> list[dict]:
    raw = row.get("shots", row.get("screenshots", row.get("images")))
    items = list(raw) if isinstance(raw, list) else []
    single = row.get("screenshot", row.get("image", row.get("截图")))
    if isinstance(single, str):
        items.append({"file": single, "caption": row.get("caption", ""), "box": row.get("box", row.get("红框"))})
    elif isinstance(single, dict):
        items.append(single)
    shots = []
    for item in items:
        if isinstance(item, str):
            item = {"file": item}
        if not isinstance(item, dict):
            continue
        file_name = item.get("file", item.get("path", item.get("image", item.get("src", ""))))
        shots.append(
            {
                "file": "" if file_name is None else str(file_name),
                "caption": redact_text(str(item.get("caption", item.get("note", item.get("说明", ""))) or "")),
                "box": parse_box(item.get("box", item.get("rect", item.get("红框")))),
            }
        )
    return shots


def image_size(data: bytes, suffix: str) -> tuple[int, int] | None:
    suf = suffix.lower()
    if suf == ".png" and data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        width, height = struct.unpack(">II", data[16:24])
        return int(width), int(height)
    if suf in {".jpg", ".jpeg"} and data.startswith(b"\xff\xd8"):
        index = 2
        length = len(data)
        while index < length - 8:
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            if marker in {0xC0, 0xC1, 0xC2}:
                height, width = struct.unpack(">HH", data[index + 5 : index + 9])
                return int(width), int(height)
            if marker in {0xD8, 0x01}:
                index += 2
                continue
            if marker in {0xD9, 0xDA}:
                break
            size = struct.unpack(">H", data[index + 2 : index + 4])[0]
            index += 2 + size
        return None
    if suf == ".gif" and len(data) >= 10 and data[:3] == b"GIF":
        width, height = struct.unpack("<HH", data[6:10])
        return int(width), int(height)
    if suf == ".webp" and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = data[12:16]
        if kind == b"VP8X" and len(data) >= 30:
            width = 1 + int.from_bytes(data[24:27], "little")
            height = 1 + int.from_bytes(data[27:30], "little")
            return width, height
        if kind == b"VP8 " and len(data) >= 30:
            width = struct.unpack("<H", data[26:28])[0] & 0x3FFF
            height = struct.unpack("<H", data[28:30])[0] & 0x3FFF
            return width, height
        if kind == b"VP8L" and len(data) >= 25:
            b0, b1, b2, b3 = data[21:25]
            width = (b0 | ((b1 & 0x3F) << 8)) + 1
            height = ((b1 >> 6) | (b2 << 2) | ((b3 & 0xF) << 10)) + 1
            return width, height
    return None


def embed(path: Path) -> tuple[str, tuple[int, int] | None] | tuple[None, None]:
    mime = IMAGE_TYPES.get(path.suffix.lower())
    if mime is None:
        return None, None
    try:
        data = path.read_bytes()
    except OSError:
        return None, None
    encoded = base64_data(data)
    return f"data:{mime};base64,{encoded}", image_size(data, path.suffix)


def base64_data(data: bytes) -> str:
    import base64

    return base64.standard_b64encode(data).decode("ascii")


def is_confirm_alias(value: str) -> bool:
    text = (value or "").strip()
    if not text or text in NOT_PASS_ALIASES or text in RESULT_ORDER:
        return False
    if text == "确认":
        return True
    return text.lower() in PASS_ALIASES


def normalize_result(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return "未填"
    if is_confirm_alias(text):
        return "通过"
    if text in RESULT_ORDER or text == "未填":
        return text
    mapped = RESULT_NORMALIZE.get(text.lower())
    return mapped or text


def parse_flag_or_label(row: dict, keys: tuple[str, ...]) -> tuple[bool, str]:
    raw = first_raw(row, keys)
    if raw in (None, ""):
        return False, ""
    if isinstance(raw, bool):
        return raw, ""
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return bool(raw), ""
    text = str(raw).strip()
    if text.lower() in TRUTHY:
        return True, ""
    if text.lower() in FALSY:
        return False, ""
    return True, redact_text(text)


def is_meta_row(row: dict) -> bool:
    kind = str(row.get("type") or row.get("record") or row.get("kind") or "").strip().lower()
    if kind in META_KIND:
        return True
    has_case = any(row.get(key) not in (None, "") for key in ID_KEYS + TITLE_KEYS + RESULT_KEYS)
    has_meta = any(row.get(key) not in (None, "") for key in PROJECT_KEYS + BATCH_KEYS + CONCLUSION_KEYS)
    return has_meta and not has_case


def is_defect(row: dict) -> bool:
    for key in BUG_MARK_KEYS:
        if key in row and truthy(row[key]):
            return True
    return row.get("result") in FAIL_RESULTS or row.get("raw_result") in {"缺陷"}


def parse_steps(value) -> list[str] | None:
    if value in (None, "", []):
        return None
    chunks: list[str] = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                text = first_text(item, ("text", "step", "说明", "content", "desc", "action"))
            else:
                text = redact_text(str(item).strip())
            text = re.sub(r"^\s*\d+\s*[\.、\)]\s*", "", text).strip()
            if text:
                chunks.append(text)
        return chunks or None
    text = redact_text(str(value).strip())
    lines = [line.strip() for line in re.split(r"\n+", text) if line.strip()]
    if len(lines) <= 1:
        pieces = re.split(r"(?:(?<=\s)|^)\d+\s*[\.、\)]\s+", text)
        chunks = [piece.strip() for piece in pieces if piece.strip()]
        return chunks or ([text] if text else None)
    for line in lines:
        chunks.append(re.sub(r"^\s*\d+\s*[\.、\)]\s*", "", line).strip())
    chunks = [item for item in chunks if item]
    return chunks or None


def field_or_missing(text: str) -> str:
    value = (text or "").strip()
    return value if value else MISSING


def marked_missing(text: str) -> str:
    value = field_or_missing(text)
    if value == MISSING:
        return f'<span class="miss">{html.escape(MISSING)}</span>'
    return html.escape(value)


def prose_blocks(text: str) -> list[str]:
    value = (text or "").strip()
    if not value:
        return []
    if "\n" in value:
        return [part.strip() for part in re.split(r"\n+", value) if part.strip()]
    parts = re.findall(r".+?(?:[。！？；][」』”’》）]*|$)", value)
    parts = [part.strip() for part in parts if part.strip()]
    return parts or [value]


def render_prose(text: str, missing: bool = True) -> str:
    blocks = prose_blocks(text)
    if not blocks:
        return f'<p class="prose">{marked_missing("") if missing else ""}</p>' if missing else ""
    return '<div class="prose">' + "".join(f"<p>{html.escape(block)}</p>" for block in blocks) + "</div>"


def parse_datetime_safe(value: str) -> datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    text = text.replace("：", ":")
    if text.endswith("Z"):
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            pass
    cleaned = re.sub(r"\s*（[^）]*）\s*$", "", text)
    cleaned = re.sub(r"\s*\([^)]*\)\s*$", "", cleaned)
    cleaned = re.sub(r"\s*(Asia/Shanghai|Asia/Taipei|UTC\+8|UTC\+08:00|上海时间|北京时间)\s*$", "", cleaned)
    cleaned = cleaned.replace("/", "-")
    match = re.match(r"^(\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?)", cleaned)
    if not match:
        try:
            parsed = datetime.fromisoformat(cleaned)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=SHANGHAI)
        except ValueError:
            return None
    piece = match.group(1).replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(piece, fmt).replace(tzinfo=SHANGHAI)
        except ValueError:
            continue
    try:
        parsed = datetime.fromisoformat(piece)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=SHANGHAI)


def format_shanghai(value: str, fallback: datetime | None = None) -> str:
    raw = (value or "").strip()
    parsed = parse_datetime_safe(raw)
    if parsed is None and fallback is not None:
        parsed = fallback if fallback.tzinfo else fallback.replace(tzinfo=SHANGHAI)
    if parsed is None:
        if not raw:
            return MISSING
        if any(token in raw for token in ("上海", "Asia/Shanghai", "UTC+8", "UTC+08")):
            return raw if "UTC+8" in raw or "上海" in raw else f"{raw}（上海时间，UTC+8）"
        return f"{raw}（上海时间，UTC+8）"
    local = parsed.astimezone(SHANGHAI)
    if re.search(r"\d{2}:\d{2}-\d{2}:\d{2}", raw):
        # keep an explicit range, but still label the zone
        cleaned = re.sub(r"\s*(Asia/Shanghai|上海时间|北京时间|UTC\+8)?\s*$", "", raw).strip()
        if "上海" in raw or "UTC+8" in raw:
            return raw if "上海" in raw else f"{cleaned}（上海时间，UTC+8）"
        return f"{cleaned}（上海时间，UTC+8）"
    clock = "%Y-%m-%d %H:%M:%S" if local.second else "%Y-%m-%d %H:%M"
    return local.strftime(clock) + "（上海时间，UTC+8）"


def empty_meta() -> dict:
    return {
        "project": "",
        "batch": "",
        "slug": "",
        "env": "",
        "side": "",
        "machine": "",
        "time": "",
        "timezone": "Asia/Shanghai",
        "conclusion": "",
        "sample": False,
        "requirement_points": [],
    }


def fill_meta(target: dict, source: dict) -> None:
    mapping = {
        "project": PROJECT_KEYS,
        "batch": BATCH_KEYS,
        "slug": SLUG_KEYS,
        "env": ENV_KEYS,
        "side": SIDE_KEYS,
        "machine": MACHINE_KEYS,
        "time": TIME_KEYS,
        "timezone": ZONE_KEYS,
        "conclusion": CONCLUSION_KEYS,
    }
    for field, keys in mapping.items():
        if not target.get(field):
            text = first_text(source, keys)
            if text:
                target[field] = text
    if not target.get("sample"):
        target["sample"] = truthy(source.get("sample") or source.get("样例") or source.get("is_sample"))
    if not target.get("requirement_points"):
        planned = first_raw(source, ("requirement_points", "需求点"))
        if isinstance(planned, list) and planned:
            target["requirement_points"] = planned
        elif isinstance(planned, str) and planned.strip():
            target["requirement_points"] = [item.strip() for item in re.split(r"[\n,，;；]", planned) if item.strip()]


def load_document(path: Path) -> tuple[dict, list[dict], int]:
    meta = empty_meta()
    rows: list[dict] = []
    skipped = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if not isinstance(raw, dict):
            skipped += 1
            continue
        if is_meta_row(raw):
            fill_meta(meta, raw)
            continue
        fill_meta(meta, raw)
        result_text = first_text(raw, RESULT_KEYS, "未填")
        row = {
            "id": first_text(raw, ID_KEYS),
            "title": first_text(raw, TITLE_KEYS),
            "raw_result": result_text,
            "result": normalize_result(result_text),
            "summary": first_text(raw, SUMMARY_KEYS),
            "shots": shot_list(raw),
            "preconditions": first_text(raw, PRE_KEYS),
            "steps": parse_steps(first_raw(raw, STEP_KEYS)),
            "expected": first_text(raw, EXPECTED_KEYS),
            "actual": first_text(raw, ACTUAL_KEYS),
            "basis": first_text(raw, BASIS_KEYS),
            "severity": first_text(raw, SEVERITY_KEYS),
            "impact": first_text(raw, IMPACT_KEYS),
            "env": first_text(raw, ENV_KEYS) or meta.get("env", ""),
            "side": first_text(raw, SIDE_KEYS) or meta.get("side", ""),
            "machine": first_text(raw, MACHINE_KEYS) or meta.get("machine", ""),
            "time": first_text(raw, TIME_KEYS) or meta.get("time", ""),
            "timezone": first_text(raw, ZONE_KEYS) or meta.get("timezone", ""),
            "is_bug_marked": any(key in raw and truthy(raw[key]) for key in BUG_MARK_KEYS),
        }
        req_hit, req_label = parse_flag_or_label(raw, REQ_POINT_KEYS)
        mismatch, _ = parse_flag_or_label(raw, REQ_MISMATCH_KEYS)
        if mismatch:
            req_hit = True
        row["requirement_point"] = req_hit
        row["requirement_label"] = req_label
        row["requirement_mismatch"] = mismatch
        row["defect"] = is_defect(row)
        rows.append(row)
    return meta, rows, skipped


def apply_meta_overrides(meta: dict, overrides: dict | None) -> dict:
    merged = dict(meta)
    if not overrides:
        return merged
    for key in empty_meta():
        value = overrides.get(key)
        if value not in (None, ""):
            merged[key] = value
    return merged


def report_name(meta: dict) -> str:
    project = (meta.get("project") or "").strip()
    batch = (meta.get("batch") or "").strip()
    slug = (meta.get("slug") or "").strip()
    if project and batch and project != batch:
        return f"{project} / {batch}"
    return batch or project or slug or "未命名批次"


def report_title(meta: dict, generated_at: datetime | None = None, kind: str = "report") -> str:
    """HTML 标题和封面用的名称：需求/批次名 + 测试时间，不用单独的「批次报告」。"""
    when = format_shanghai(meta.get("time") or "", generated_at)
    title = f"{report_name(meta)} · {when}"
    if kind == "bugs":
        return f"缺陷文档：{title}"
    return title


def safe_slug(text: str, fallback: str = "weiming-pici") -> str:
    value = (text or "").strip()
    for src, dst in (
        ("　", "-"),
        (" ", "-"),
        ("/", "-"),
        ("\\", "-"),
        ("·", "-"),
        ("—", "-"),
        ("–", "-"),
    ):
        value = value.replace(src, dst)
    value = re.sub(r"[^\w.-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    value = value.strip(".-")
    if not value:
        value = fallback
    return value[:80]


def stamp_datetime(meta: dict, fallback: datetime | None = None) -> datetime:
    parsed = parse_datetime_safe(meta.get("time") or "")
    if parsed is None:
        parsed = fallback or datetime.now(tz=SHANGHAI)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=SHANGHAI)
    return parsed.astimezone(SHANGHAI)


def compact_stamp(meta: dict, fallback: datetime | None = None) -> str:
    return stamp_datetime(meta, fallback).strftime("%Y%m%d-%H%M")


def file_prefix(meta: dict, fallback: datetime | None = None) -> str:
    raw = (meta.get("slug") or meta.get("batch") or meta.get("project") or "").strip()
    return f"{safe_slug(raw)}-{compact_stamp(meta, fallback)}"


def default_filenames(meta: dict, fallback: datetime | None = None) -> dict:
    prefix = file_prefix(meta, fallback)
    return {
        "prefix": prefix,
        "report": f"{prefix}-report.html",
        "bugs": f"{prefix}-bugs.html",
        "bugs_md": f"{prefix}-bugs.md",
    }


def filenames_for_report(report_path: Path, meta: dict, fallback: datetime | None = None) -> dict:
    """按主报告路径推导同一次收工的缺陷文档名。未指定 -o 时用需求简称+时间自动起名。"""
    name = report_path.name
    if name.endswith("-report.html"):
        prefix = name[: -len("-report.html")]
    else:
        prefix = report_path.stem or file_prefix(meta, fallback)
    return {
        "prefix": prefix,
        "report": name,
        "bugs": f"{prefix}-bugs.html",
        "bugs_md": f"{prefix}-bugs.md",
    }


def confirm_count(rows: list[dict]) -> int:
    return sum(1 for row in rows if is_confirm_alias(row.get("raw_result") or ""))


def count_text(rows: list[dict]) -> str:
    counts: Counter[str] = Counter(row["result"] for row in rows)
    parts = []
    folded = confirm_count(rows)
    for name in RESULT_ORDER:
        number = counts.get(name, 0)
        if name == "通过" and folded:
            parts.append(f"通过 {number}（含确认 {folded}）")
        else:
            parts.append(f"{name} {number}")
    for name, number in counts.items():
        if name not in RESULT_ORDER:
            parts.append(f"{name} {number}")
    return "，".join(parts)


def result_counts(rows: list[dict]) -> Counter[str]:
    return Counter(row["result"] for row in rows)


def case_sort_key(row: dict, index: int) -> tuple:
    return (
        0 if row.get("requirement_mismatch") else 1,
        0 if row.get("requirement_point") else 1,
        index,
    )


def grouped_rows(rows: list[dict]) -> list[tuple[str, list[dict]]]:
    buckets: dict[str, list[tuple[int, dict]]] = {}
    seen: list[str] = []
    for index, row in enumerate(rows):
        name = row["result"] or "未填"
        if name not in buckets:
            buckets[name] = []
            seen.append(name)
        buckets[name].append((index, row))

    def ordered(items: list[tuple[int, dict]]) -> list[dict]:
        return [row for _, row in sorted(items, key=lambda item: case_sort_key(item[1], item[0]))]

    groups: list[tuple[str, list[dict]]] = []
    for name in RESULT_ORDER:
        if name in buckets:
            groups.append((name, ordered(buckets[name])))
    for name in seen:
        if name not in RESULT_ORDER:
            groups.append((name, ordered(buckets[name])))
    return groups


def style_name(name: str) -> str:
    return name if name in KNOWN_RESULT_STYLES else "其他"


def requirement_rows(rows: list[dict]) -> list[dict]:
    return [row for row in rows if row.get("requirement_point")]


def coverage_info(rows: list[dict], meta: dict) -> dict:
    reqs = requirement_rows(rows)
    untested_states = {"未测", "未填"}
    tested = [row for row in reqs if row["result"] not in untested_states]
    untested = [row for row in reqs if row["result"] in untested_states]
    failed = [row for row in reqs if row["result"] == "失败"]
    blocked = [row for row in reqs if row["result"] == "阻塞"]
    mismatch = [row for row in rows if row.get("requirement_mismatch")]
    extras_tested = [
        row
        for row in rows
        if not row.get("requirement_point") and row["result"] not in untested_states
    ]
    return {
        "reqs": reqs,
        "tested": tested,
        "untested": untested,
        "failed": failed,
        "blocked": blocked,
        "mismatch": mismatch,
        "priority_gap": bool(untested and extras_tested),
        "planned": meta.get("requirement_points") or [],
    }


def case_heading(row: dict, index: int) -> str:
    title = " ".join(part for part in (row.get("id"), row.get("title")) if part)
    return title or f"第 {index} 条"


def case_anchor(row: dict, index: int) -> str:
    base = row.get("id") or f"case-{index}"
    slug = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fff-]+", "-", str(base)).strip("-")
    return f"item-{slug or index}"


def environment_text(row: dict | None, meta: dict) -> str:
    source = row or {}
    parts = []
    site = source.get("env") or meta.get("env") or ""
    side = source.get("side") or meta.get("side") or ""
    when = format_shanghai(source.get("time") or meta.get("time") or "")
    machine = source.get("machine") or meta.get("machine") or ""
    if site:
        parts.append(site)
    if side:
        parts.append(side)
    if when and when != MISSING:
        parts.append(when)
    if machine:
        parts.append(f"机器：{machine}")
    return "；".join(parts)


def impact_text(row: dict) -> str:
    severity = (row.get("severity") or "").strip()
    impact = (row.get("impact") or "").strip()
    if severity and impact:
        return f"严重程度：{severity}。影响：{impact}"
    return severity or impact


def expected_with_basis(row: dict) -> str:
    expected = (row.get("expected") or "").strip()
    basis = (row.get("basis") or "").strip()
    basis_note = basis if basis else MISSING
    if not expected:
        return ""
    if "依据" in expected:
        return expected
    if basis:
        return f"{expected}\n挂靠依据：{basis_note}（详见「依据」栏）。"
    return f"{expected}\n挂靠依据：{MISSING}。"


def md_escape(text: str) -> str:
    return re.sub(r"([\\`*_{}\[\]()#+])", r"\\\1", text or "")


def html_head(title: str) -> list[str]:
    return [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{html.escape(title)}</title>",
        "<style>",
        SHARED_CSS,
        "</style>",
        "</head>",
        "<body>",
        '<div class="page">',
    ]


def resolve_shot(root: Path, shot: dict) -> Path | None:
    if not shot.get("file"):
        return None
    candidate = Path(shot["file"])
    if not candidate.is_absolute():
        candidate = root / candidate
    if not inside(candidate, root):
        return None
    return candidate


def render_shot_figure(root: Path, shot: dict, key: str, notes: list[str], owner: str) -> str:
    caption = shot.get("caption") or "缺白话说明"
    candidate = resolve_shot(root, shot)
    if candidate is None:
        notes.append(f"{owner} 有一张图没有嵌入（路径须在本批目录内，且不能是 secrets 或 leases）")
        return (
            f'<figure class="shot"><figcaption>{html.escape(caption)}</figcaption></figure>'
        )
    uri, size = embed(candidate)
    if uri is None:
        notes.append(f"{owner} 的图片不是可嵌入的 png、jpg、gif 或 webp")
        return f'<figure class="shot"><figcaption>{html.escape(caption)}</figcaption></figure>'

    box_html = ""
    sizer_style = "max-width:720px"
    if size:
        width, height = size
        sizer_style = f"max-width:min(720px, {width}px)"
        if shot.get("box") is not None:
            left, top, box_w, box_h = shot["box"]
            box_html = (
                f'<i class="shot-box" style="left:{left / width * 100:.4f}%;'
                f"top:{top / height * 100:.4f}%;width:{box_w / width * 100:.4f}%;"
                f'height:{box_h / height * 100:.4f}%"></i>'
            )
    elif shot.get("box") is not None:
        left, top, box_w, box_h = shot["box"]
        # 不知道原图尺寸时不缩放，避免红框错位
        sizer_style = "max-width:100%;overflow:auto"
        box_html = f'<i class="shot-box" style="left:{left}px;top:{top}px;width:{box_w}px;height:{box_h}px"></i>'

    return "\n".join(
        [
            '<figure class="shot">',
            f'<div class="shot-sizer" style="{sizer_style}">',
            f'<button type="button" class="shot-frame shot-open-area" data-shot="{html.escape(key)}" aria-label="查看原图：{html.escape(caption)}">',
            f'<img alt="{html.escape(caption)}" src="{uri}">',
            box_html,
            "</button>",
            f'<p><button type="button" class="shot-open" data-shot="{html.escape(key)}">点击查看原图</button></p>',
            "</div>",
            f"<figcaption>{html.escape(caption)}</figcaption>",
            "</figure>",
        ]
    )


SHOT_JS = """
(function () {
  var dialog = document.getElementById("shot-dialog");
  var image = document.getElementById("shot-dialog-img");
  var caption = document.getElementById("shot-dialog-cap");
  if (!dialog || !image) return;
  function close() { if (dialog.open) dialog.close(); }
  document.querySelectorAll("[data-shot]").forEach(function (el) {
    el.addEventListener("click", function (ev) {
      ev.preventDefault();
      var frame = el.closest(".shot-sizer") || el;
      var pic = frame.querySelector("img");
      if (!pic) return;
      image.src = pic.src;
      image.alt = pic.alt || "原图";
      if (caption) caption.textContent = pic.alt || "";
      if (dialog.showModal) dialog.showModal();
    });
  });
  var closer = document.getElementById("shot-dialog-close");
  if (closer) closer.addEventListener("click", close);
  dialog.addEventListener("click", function (ev) { if (ev.target === dialog) close(); });
})();
"""

FILTER_JS = """
(function () {
  var bar = document.querySelector(".filters");
  if (!bar) return;
  bar.hidden = false;
  function apply(name) {
    bar.querySelectorAll("button[data-filter]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", btn.getAttribute("data-filter") === name ? "true" : "false");
    });
    document.querySelectorAll(".case").forEach(function (card) {
      var match = name === "all" || card.getAttribute("data-result") === name;
      card.hidden = !match;
    });
    document.querySelectorAll(".group").forEach(function (group) {
      var visible = group.querySelector(".case:not([hidden])");
      group.hidden = !visible;
    });
  }
  bar.addEventListener("click", function (ev) {
    var btn = ev.target.closest("button[data-filter]");
    if (!btn) return;
    apply(btn.getAttribute("data-filter"));
  });
})();
"""


def shot_dialog_html() -> list[str]:
    return [
        '<dialog id="shot-dialog">',
        '<div class="dialog-bar"><strong>原图</strong>',
        '<button type="button" id="shot-dialog-close">关闭</button></div>',
        '<img id="shot-dialog-img" alt="原图">',
        '<p id="shot-dialog-cap" class="shot-cap"></p>',
        "</dialog>",
        "<script>",
        SHOT_JS,
        FILTER_JS,
        "</script>",
    ]
