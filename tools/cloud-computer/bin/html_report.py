#!/usr/bin/env python3
"""把本批 results.jsonl 收成一份自带原图的 HTML 报告。

批次收尾技能直接运行：

  python3 /workspace/qa/bin/html_report.py

当前目录有 results.jsonl 时，写出同目录的 report.html。也可以指定路径：

  python3 html_report.py path/to/results.jsonl -o path/to/report.html

每行一个 JSON 对象，用到的字段：

  {"id": "用例编号", "title": "名称", "result": "失败", "summary": "一句白话",
   "shots": [{"file": "step.png", "caption": "红框旁边的白话", "box": [x, y, w, h]}]}

图片路径相对 results.jsonl 所在目录，必须落在这个目录里面。脚本把图片转成 data URI 嵌进 HTML，
不引用外链。box 是原图像素坐标，报告里用红框叠在图上，白话写在图旁。
密码、验证码、token 会换成 ***。不读 secrets 或 leases 目录，也不把整份原始 JSON 打进报告。
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

RESULT_ORDER = ("通过", "失败", "阻塞", "未测", "未验证", "已跑待评审", "已跑待确认")
IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}
SECRET_TEXT = (
    (re.compile(r"(?i)\b(bearer)\s+\S+"), r"\1 ***"),
    (re.compile(r"(?i)\b(password|passwd|pwd|token|secret|cookie|authorization|otp)\b\s*[:=]\s*\S+"), r"\1=***"),
    (re.compile(r"(验证码|密码|口令)\s*[:=：]\s*\S+"), r"\1=***"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"), "***"),
)
BLOCKED_PARTS = {"secrets", "leases"}


def redact_text(value: str) -> str:
    for pattern, repl in SECRET_TEXT:
        value = pattern.sub(repl, value)
    return value


def first_text(row: dict, keys: tuple[str, ...], default: str = "") -> str:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return redact_text(str(row[key]))
    return default


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


def load_rows(path: Path) -> tuple[list[dict], int]:
    rows = []
    skipped = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if not isinstance(row, dict):
            skipped += 1
            continue
        rows.append(
            {
                "id": first_text(row, ("id", "编号", "case_id")),
                "title": first_text(row, ("title", "名称", "name")),
                "result": first_text(row, ("result", "结果", "status"), "未填"),
                "summary": first_text(row, ("summary", "note", "说明", "caption")),
                "shots": shot_list(row),
            }
        )
    return rows, skipped


def embed(path: Path) -> str | None:
    mime = IMAGE_TYPES.get(path.suffix.lower())
    if mime is None:
        return None
    try:
        data = path.read_bytes()
    except OSError:
        return None
    encoded = base64.standard_b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render(rows: list[dict], root: Path, skipped: int) -> tuple[str, str]:
    counts: Counter[str] = Counter(row["result"] for row in rows)
    count_text = "，".join(f"{name} {counts.get(name, 0)}" for name in RESULT_ORDER)
    other = sum(number for name, number in counts.items() if name not in RESULT_ORDER)
    if other:
        count_text += f"，其他 {other}"

    parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>批次报告</title>",
        "<style>",
        "body { font: 16px/1.5 sans-serif; margin: 24px; color: #1a1a1a; }",
        "h1 { font-size: 22px; }",
        ".case { border-top: 1px solid #ddd; padding: 16px 0; }",
        ".result { font-weight: 700; }",
        ".shot { display: flex; align-items: flex-start; gap: 16px; margin: 12px 0; }",
        ".frame-wrap { overflow: auto; max-width: 70%; }",
        ".frame { position: relative; display: inline-block; }",
        ".frame img { display: block; }",
        ".box { position: absolute; border: 3px solid #d00000; box-sizing: border-box; pointer-events: none; }",
        "figcaption { margin: 0; max-width: 36em; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>批次报告</h1>",
        f"<p>{html.escape(count_text)}。</p>",
        "<p>图片已嵌进本文件。密码、验证码和 token 已写成 ***。报告不引用外链。</p>",
    ]
    notes = []
    for index, row in enumerate(rows, start=1):
        title = " ".join(part for part in (row["id"], row["title"]) if part) or f"第 {index} 条"
        summary = row["summary"] or "缺白话说明"
        parts.append('<section class="case">')
        parts.append(f"<h2>{html.escape(title)}</h2>")
        parts.append(f'<p class="result">{html.escape(row["result"])}</p>')
        parts.append(f"<p>{html.escape(summary)}</p>")
        if not row["shots"]:
            parts.append("</section>")
            continue
        for shot in row["shots"]:
            caption = shot["caption"] or "缺白话说明"
            candidate = Path(shot["file"])
            if not candidate.is_absolute():
                candidate = root / candidate
            if not shot["file"] or not inside(candidate, root):
                notes.append(f"{title} 有一张图没有嵌入（路径须在本批目录内，且不能是 secrets 或 leases）")
                parts.append('<figure class="shot">')
                parts.append(f"<figcaption>{html.escape(caption)}</figcaption>")
                parts.append("</figure>")
                continue
            uri = embed(candidate)
            if uri is None:
                notes.append(f"{title} 的图片不是可嵌入的 png、jpg、gif 或 webp")
                parts.append('<figure class="shot">')
                parts.append(f"<figcaption>{html.escape(caption)}</figcaption>")
                parts.append("</figure>")
                continue
            box = ""
            if shot["box"] is not None:
                left, top, width, height = shot["box"]
                box = f'<i class="box" style="left:{left}px;top:{top}px;width:{width}px;height:{height}px"></i>'
            parts.append('<figure class="shot">')
            parts.append('<div class="frame-wrap"><div class="frame">')
            parts.append(f'<img alt="" src="{uri}">')
            parts.append(box)
            parts.append("</div></div>")
            parts.append(f"<figcaption>{html.escape(caption)}</figcaption>")
            parts.append("</figure>")
        parts.append("</section>")
    if skipped:
        notes.append(f"跳过 {skipped} 行无法解析的内容")
    if notes:
        parts.append("<h2>生成时跳过的项</h2><ul>")
        parts.extend(f"<li>{html.escape(note)}</li>" for note in notes)
        parts.append("</ul>")
    parts.append("</body></html>")
    return "\n".join(parts) + "\n", count_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="把 results.jsonl 收成自带原图的 HTML 报告。")
    parser.add_argument("results", nargs="?", help="默认是当前目录的 results.jsonl")
    parser.add_argument("-o", "--output", help="默认写到 results.jsonl 同目录的 report.html")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    source = Path(args.results) if args.results else Path.cwd() / "results.jsonl"
    if forbidden(source) or not source.is_file():
        print(f"html_report: 找不到可用的结果文件 {source}", file=sys.stderr)
        print("用法: python3 html_report.py [results.jsonl] [-o report.html]", file=sys.stderr)
        return 2
    root = source.parent.resolve()
    dest = Path(args.output) if args.output else root / "report.html"
    if forbidden(dest):
        print("html_report: 不把报告写进 secrets 或 leases", file=sys.stderr)
        return 2

    rows, skipped = load_rows(source)
    if not rows:
        print("html_report: results.jsonl 里没有可用记录", file=sys.stderr)
        return 2
    document, count_text = render(rows, root, skipped)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(document, encoding="utf-8")
    print(f"report: {dest}")
    print(count_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
