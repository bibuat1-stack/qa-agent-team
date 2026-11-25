#!/usr/bin/env python3
"""把本批缺陷收成独立的缺陷文档（与主报告同一前缀）。

通常由 html_report.py 一并调用。也可以单独运行：

  python3 bug_report.py path/to/results.jsonl

默认按「需求简称-测试时间-bugs.html」和同前缀的 bugs.md 写出。
本批没有缺陷就不出文件。缺陷指结果为「失败」，或条目明确标了是缺陷。
「阻塞」「已跑待确认」不单独装订，除非该条明确标了是缺陷。

每一条缺陷都分栏写出：标题、环境、前置条件、复现步骤、预期结果、依据、
实际结果、影响与严重程度、截图/证据。缺的栏写「缺，待补」，不省略，不编造依据。
预期结果会挂靠依据，不只写现象。与需求不符的缺陷排在前面，并醒目标记。
"""
from __future__ import annotations

import argparse
import html
import sys
from datetime import datetime
from pathlib import Path

from report_common import (
    MISSING,
    SHANGHAI,
    apply_meta_overrides,
    case_anchor,
    case_heading,
    case_sort_key,
    default_filenames,
    environment_text,
    expected_with_basis,
    field_or_missing,
    format_shanghai,
    forbidden,
    html_head,
    impact_text,
    load_document,
    marked_missing,
    md_escape,
    render_prose,
    render_shot_figure,
    report_title,
    shot_dialog_html,
    style_name,
)


def defect_rows(rows: list[dict]) -> list[dict]:
    bugs = [row for row in rows if row.get("defect")]
    return [row for _, row in sorted(enumerate(bugs), key=lambda item: case_sort_key(item[1], item[0]))]


def clear_bug_docs(directory: Path, names: dict | None = None) -> list[Path]:
    removed = []
    candidates = []
    if names:
        candidates.extend([names.get("bugs") or "", names.get("bugs_md") or ""])
    for name in candidates:
        if not name:
            continue
        path = directory / name
        if path.is_file() and not forbidden(path):
            path.unlink()
            removed.append(path)
    return removed


def write_bug_docs(
    rows: list[dict],
    meta: dict,
    root: Path,
    dest_dir: Path,
    generated_at: datetime | None = None,
    names: dict | None = None,
) -> tuple[Path, Path] | None:
    bugs = defect_rows(rows)
    if not bugs:
        return None
    when = generated_at or datetime.now(tz=SHANGHAI)
    dest_dir.mkdir(parents=True, exist_ok=True)
    names = names or default_filenames(meta, when)
    html_path = dest_dir / names["bugs"]
    md_path = dest_dir / names["bugs_md"]
    if forbidden(html_path) or forbidden(md_path):
        raise SystemExit("bug_report: 不把缺陷文档写进 secrets 或 leases")
    report_name = names.get("report") or f"{names.get('prefix', 'batch')}-report.html"
    html_path.write_text(render_bugs_html(bugs, meta, root, when, report_name, names["bugs_md"]), encoding="utf-8")
    md_path.write_text(render_bugs_md(bugs, meta, root, when, report_name, names["bugs_md"]), encoding="utf-8")
    return html_path, md_path


def render_env_cell(row: dict, meta: dict) -> str:
    text = environment_text(row, meta)
    return field_or_missing(text)


def render_steps_html(row: dict) -> str:
    steps = row.get("steps")
    if not steps:
        return marked_missing("")
    items = "".join(f"<li>{html.escape(step)}</li>" for step in steps)
    return f'<ol class="ol-steps">{items}</ol>'


def render_steps_md(row: dict) -> str:
    steps = row.get("steps")
    if not steps:
        return MISSING
    return "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))


def bug_tags(row: dict) -> str:
    tags = []
    result = row.get("result") or "失败"
    tags.append(f'<span class="tag tag-{html.escape(style_name(result))}">{html.escape(result)}</span>')
    if row.get("requirement_mismatch"):
        tags.append('<span class="tag tag-与需求不符">与需求不符</span>')
    elif row.get("requirement_point"):
        tags.append('<span class="tag tag-需求点">需求点</span>')
    return " ".join(tags)


def render_bugs_html(
    bugs: list[dict],
    meta: dict,
    root: Path,
    generated_at: datetime,
    report_name: str,
    bugs_md_name: str,
) -> str:
    title = report_title(meta, generated_at, kind="bugs")
    notes: list[str] = []
    parts = html_head(title)
    if meta.get("sample"):
        parts.append('<p class="banner">本页是缺陷文档样例，数据已经脱敏，不是一次真实测试的结论。依据如为示例出处，已在栏内标明。</p>')
    parts.append(f"<h1>{html.escape(title)}</h1>")
    when = format_shanghai(meta.get("time") or "", generated_at)
    env_line = "；".join(
        part
        for part in (
            meta.get("env"),
            meta.get("side"),
            f"机器：{meta['machine']}" if meta.get("machine") else "",
        )
        if part
    )
    parts.append(f'<p class="meta">测试时间：{html.escape(when)}</p>')
    if env_line:
        parts.append(f'<p class="meta">环境：{html.escape(env_line)}</p>')
    mismatch_n = sum(1 for row in bugs if row.get("requirement_mismatch"))
    parts.append(
        f'<p class="meta">共 {len(bugs)} 条缺陷'
        + (f'，其中 {mismatch_n} 条与需求不符，已排在前面' if mismatch_n else "")
        + f'。正报告：<a href="{html.escape(report_name)}">{html.escape(report_name)}</a>'
        + (f'；Markdown：<a href="{html.escape(bugs_md_name)}">{html.escape(bugs_md_name)}</a>' if bugs_md_name else "")
        + "</p>"
    )
    parts.append(
        '<section class="conclusion"><p>每条缺陷都单独写清前置条件、复现步骤、预期结果、'
        "依据和实际结果。依据必须写出处（需求文档位置加原文一句、约定俗成，或其他依据）；"
        "没有依据就写「缺，待补」，不编造。与需求不符的条目会醒目标记，并同样写清依据。</p></section>"
    )
    parts.append('<nav class="toc"><h2>目录</h2><ol>')
    for index, row in enumerate(bugs, start=1):
        anchor = case_anchor(row, index)
        heading = case_heading(row, index)
        parts.append(f'<li><a href="#{html.escape(anchor)}">{html.escape(heading)}</a> {bug_tags(row)}</li>')
    parts.append("</ol></nav>")

    for index, row in enumerate(bugs, start=1):
        anchor = case_anchor(row, index)
        heading = case_heading(row, index)
        classes = "bug mismatch" if row.get("requirement_mismatch") else "bug"
        parts.append(f'<article class="{classes}" id="{html.escape(anchor)}">')
        parts.append('<div class="case-head">')
        parts.append(f"<h3>{html.escape(heading)}</h3>")
        parts.append(bug_tags(row))
        parts.append("</div>")
        parts.append('<dl class="dl">')
        parts.append("<dt>标题</dt>")
        parts.append(f"<dd>{html.escape(heading)}</dd>")
        parts.append("<dt>环境</dt>")
        parts.append(f"<dd>{marked_missing(render_env_cell(row, meta))}</dd>")
        parts.append("<dt>前置条件</dt>")
        parts.append(f"<dd>{render_prose(row.get('preconditions') or '', missing=True)}</dd>")
        parts.append("<dt>复现步骤</dt>")
        parts.append(f"<dd>{render_steps_html(row)}</dd>")
        parts.append("<dt>预期结果</dt>")
        parts.append(f"<dd>{render_prose(expected_with_basis(row), missing=True)}</dd>")
        parts.append("<dt>依据</dt>")
        basis = (row.get("basis") or "").strip()
        parts.append(f"<dd>{render_prose(basis, missing=True) if basis else marked_missing('')}</dd>")
        if row.get("actual"):
            actual = row["actual"]
        elif row.get("summary"):
            actual = row["summary"]
        else:
            actual = ""
        parts.append("<dt>实际结果</dt>")
        parts.append(f"<dd>{render_prose(actual, missing=True)}</dd>")
        parts.append("<dt>影响与严重程度</dt>")
        parts.append(f"<dd>{render_prose(impact_text(row), missing=True)}</dd>")
        parts.append("<dt>截图 / 证据</dt>")
        parts.append("<dd>")
        if not row.get("shots"):
            parts.append(marked_missing(""))
        else:
            for shot_index, shot in enumerate(row["shots"], start=1):
                parts.append(render_shot_figure(root, shot, f"{anchor}-{shot_index}", notes, heading))
        parts.append("</dd>")
        parts.append("</dl>")
        parts.append("</article>")

    if notes:
        parts.append('<section class="notes"><h2>生成时跳过的项</h2><ul>')
        parts.extend(f"<li>{html.escape(note)}</li>" for note in notes)
        parts.append("</ul></section>")
    generated = format_shanghai("", generated_at)
    parts.append(
        f'<p class="footer">缺陷文档生成于 {html.escape(generated)}。图片已嵌进本文件，无外链。'
        "密码、验证码和 token 已写成 ***。依据栏未填写的一律标为「缺，待补」。</p>"
    )
    parts.append("</div>")
    parts.extend(shot_dialog_html())
    parts.append("</body></html>")
    return "\n".join(parts) + "\n"


def render_bugs_md(
    bugs: list[dict],
    meta: dict,
    root: Path,
    generated_at: datetime,
    report_name: str,
    bugs_md_name: str,
) -> str:
    title = report_title(meta, generated_at, kind="bugs")
    lines = [f"# {title}", ""]
    if meta.get("sample"):
        lines.extend(["> 本页是缺陷文档样例，数据已经脱敏，不是一次真实测试的结论。", ""])
    when = format_shanghai(meta.get("time") or "", generated_at)
    env_line = "；".join(
        part
        for part in (
            meta.get("env"),
            meta.get("side"),
            f"机器：{meta['machine']}" if meta.get("machine") else "",
        )
        if part
    )
    mismatch_n = sum(1 for row in bugs if row.get("requirement_mismatch"))
    lines.append(f"- 测试时间：{when}")
    if env_line:
        lines.append(f"- 环境：{env_line}")
    lines.append(f"- 共 {len(bugs)} 条缺陷。正报告：`{report_name}`")
    if mismatch_n:
        lines.append(f"- 其中 {mismatch_n} 条与需求不符，已排在前面。")
    lines.append("")
    lines.append("每一条都单独写清前置条件、复现步骤、预期结果、依据和实际结果。依据必须写出处；没有就写「缺，待补」，不编造。")
    lines.append("")
    for index, row in enumerate(bugs, start=1):
        heading = case_heading(row, index)
        marks = []
        if row.get("requirement_mismatch"):
            marks.append("与需求不符")
        elif row.get("requirement_point"):
            marks.append("需求点")
        mark_text = f"（{'，'.join(marks)}）" if marks else ""
        lines.append(f"## {index}. {heading}{mark_text}")
        lines.append("")
        lines.append(f"- 结果：{row.get('result') or '失败'}")
        if row.get("requirement_mismatch"):
            lines.append("- 标记：与需求不符")
        lines.append("")
        lines.append("### 标题")
        lines.append("")
        lines.append(heading)
        lines.append("")
        lines.append("### 环境")
        lines.append("")
        lines.append(field_or_missing(environment_text(row, meta)))
        lines.append("")
        lines.append("### 前置条件")
        lines.append("")
        lines.append(field_or_missing(row.get("preconditions") or ""))
        lines.append("")
        lines.append("### 复现步骤")
        lines.append("")
        lines.append(render_steps_md(row))
        lines.append("")
        lines.append("### 预期结果")
        lines.append("")
        lines.append(field_or_missing(expected_with_basis(row)))
        lines.append("")
        lines.append("### 依据")
        lines.append("")
        lines.append(field_or_missing(row.get("basis") or ""))
        lines.append("")
        lines.append("### 实际结果")
        if row.get("actual"):
            actual = row["actual"]
        elif row.get("summary"):
            actual = row["summary"]
        else:
            actual = ""
        lines.append("")
        lines.append(field_or_missing(actual))
        lines.append("")
        lines.append("### 影响与严重程度")
        lines.append("")
        lines.append(field_or_missing(impact_text(row)))
        lines.append("")
        lines.append("### 截图 / 证据")
        lines.append("")
        if not row.get("shots"):
            lines.append(MISSING)
        else:
            for shot in row["shots"]:
                caption = shot.get("caption") or "缺白话说明"
                rel = shot.get("file") or ""
                if rel:
                    lines.append(f"![{md_escape(caption)}]({rel})")
                    lines.append("")
                lines.append(caption)
                lines.append("")
        lines.append("")
    generated = format_shanghai("", generated_at)
    lines.append("---")
    lines.append("")
    lines.append(f"文档生成于 {generated}。密码、验证码和 token 已写成 ***。依据栏未填写的一律标为「缺，待补」。")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="把 results.jsonl 里的缺陷收成与主报告同一前缀的缺陷文档。")
    parser.add_argument("results", nargs="?", help="默认是当前目录的 results.jsonl")
    parser.add_argument("-o", "--output-dir", help="默认写到 results.jsonl 同目录")
    parser.add_argument("--project")
    parser.add_argument("--batch")
    parser.add_argument("--slug")
    parser.add_argument("--env")
    parser.add_argument("--time")
    parser.add_argument("--conclusion")
    parser.add_argument("--machine")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    source = Path(args.results) if args.results else Path.cwd() / "results.jsonl"
    if forbidden(source) or not source.is_file():
        print(f"bug_report: 找不到可用的结果文件 {source}", file=sys.stderr)
        return 2
    root = source.parent.resolve()
    dest_dir = Path(args.output_dir) if args.output_dir else root
    if forbidden(dest_dir):
        print("bug_report: 不把缺陷文档写进 secrets 或 leases", file=sys.stderr)
        return 2

    meta, rows, _skipped = load_document(source)
    meta = apply_meta_overrides(
        meta,
        {
            "project": args.project,
            "batch": args.batch,
            "slug": args.slug,
            "env": args.env,
            "time": args.time,
            "conclusion": args.conclusion,
            "machine": args.machine,
        },
    )
    if not rows:
        print("bug_report: results.jsonl 里没有可用记录", file=sys.stderr)
        return 2
    generated_at = datetime.now(tz=SHANGHAI)
    stamp_fallback = generated_at
    if not (meta.get("time") or "").strip():
        try:
            stamp_fallback = datetime.fromtimestamp(source.stat().st_mtime, tz=SHANGHAI)
        except OSError:
            pass
    names = default_filenames(meta, stamp_fallback)
    written = write_bug_docs(rows, meta, root, dest_dir, generated_at, names)
    if not written:
        removed = clear_bug_docs(dest_dir, names)
        print("bug_report: 本批没有缺陷，不出缺陷文档")
        for path in removed:
            print(f"bugs_cleared: {path}")
        return 0
    bug_html, bug_md = written
    print(f"bugs: {bug_html}")
    print(f"bugs_md: {bug_md}")
    print(f"缺陷 {len(defect_rows(rows))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
