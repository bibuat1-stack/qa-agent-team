#!/usr/bin/env python3
"""把本批 results.jsonl 收成一份给人看的、自带原图的 HTML 报告。

批次收尾技能直接运行：

  python3 /workspace/qa/bin/html_report.py

当前目录有 results.jsonl 时，按「需求简称-测试时间-report.html」写到同目录。
时间用上海时间（Asia/Shanghai，UTC+8），格式如 20261126-0311。也可以用 -o 指定路径或目录：

  python3 html_report.py path/to/results.jsonl
  python3 html_report.py path/to/results.jsonl -o path/to/自定义.html

本批若有缺陷（结果为「失败」，或条目明确标了是缺陷），同目录再用同一前缀写出
「简称-时间-bugs.html」和「简称-时间-bugs.md」。没有缺陷就不出这两份文件。
同一前缀若有上次留下的缺陷文档、且本批已无缺陷，会删掉以免误认。

每行一个 JSON 对象。旧字段仍然可用：

  {"id": "用例编号", "title": "名称", "result": "失败", "summary": "一句白话",
   "shots": [{"file": "step.png", "caption": "红框旁边的白话", "box": [x, y, w, h]}]}

可选的批次元数据，可用单独一行 {"type": "meta", ...}，也可写在用例上：

  project/项目, batch/批次, slug/简称, environment/env/环境, side/前后台,
  machine/机器, time/测试时间, timezone/时区, conclusion/结论,
  requirement_points/需求点

结果「确认」计为通过；「已跑待确认」和「部分确认」不合并进通过。
未知状态按实际名称列出，不写成含糊的「其他」。

缺陷条目还可收：preconditions/前置条件, steps/复现步骤, expected/预期结果,
actual/实际结果, basis/依据/source, severity/严重程度, impact/影响,
is_bug/是缺陷, requirement_point/是需求点, requirement_mismatch/与需求不符。
中英文键名都能读。缺的栏在缺陷文档里写「缺，待补」，不编造依据。

图片路径相对 results.jsonl 所在目录，必须落在这个目录里面。脚本把图片转成 data URI 嵌进 HTML，
不引用外链。box 是原图像素坐标，报告里用红框叠在图上，白话写在图旁。
密码、验证码、token 会换成 ***。不读 secrets 或 leases 目录，也不把整份原始 JSON 打进报告。
"""
from __future__ import annotations

import argparse
import html
import sys
from datetime import datetime
from pathlib import Path

from bug_report import clear_bug_docs, write_bug_docs
from report_common import (
    RESULT_ORDER,
    SHANGHAI,
    apply_meta_overrides,
    case_anchor,
    case_heading,
    confirm_count,
    count_text,
    coverage_info,
    default_filenames,
    filenames_for_report,
    format_shanghai,
    forbidden,
    grouped_rows,
    html_head,
    is_confirm_alias,
    load_document,
    report_title,
    result_counts,
    render_prose,
    render_shot_figure,
    shot_dialog_html,
    style_name,
)


def badge(name: str, number: int, extra: str = "") -> str:
    cls = style_name(name)
    label = f"{name} {number}"
    if extra:
        label = f"{label}{extra}"
    return f'<span class="badge badge-{html.escape(cls)}">{html.escape(label)}</span>'


def case_tags(row: dict) -> list[str]:
    tags = []
    result = row.get("result") or "未填"
    tags.append(f'<span class="tag tag-{html.escape(style_name(result))}">{html.escape(result)}</span>')
    raw = row.get("raw_result") or ""
    if is_confirm_alias(raw) and result == "通过":
        tags.append(f'<span class="tag tag-原结果">原结果：{html.escape(raw)}</span>')
    if row.get("requirement_mismatch"):
        tags.append('<span class="tag tag-与需求不符">与需求不符</span>')
    elif row.get("requirement_point"):
        tags.append('<span class="tag tag-需求点">需求点</span>')
    if row.get("defect") and result != "失败":
        tags.append('<span class="tag tag-失败">缺陷</span>')
    return tags


def render_coverage(rows: list[dict], meta: dict) -> list[str]:
    info = coverage_info(rows, meta)
    if not info["reqs"] and not info["planned"] and not info["mismatch"]:
        return [
            '<section class="reqbox">',
            "<h2>需求点覆盖</h2>",
            "<p>本批结果没有标明哪些是需求正文里的点。收工前应标出需求点，并优先测完这些条目。</p>",
            "</section>",
        ]
    parts = ['<section class="reqbox' + (" warn" if info["priority_gap"] or info["untested"] else "") + '">']
    parts.append("<h2>需求点覆盖</h2>")
    total = len(info["reqs"])
    parts.append(
        f"<p>需求点 {total} 条：已测 {len(info['tested'])}，未测 {len(info['untested'])}，"
        f"失败 {len(info['failed'])}，阻塞 {len(info['blocked'])}，"
        f"与需求不符 {len(info['mismatch'])}。</p>"
    )
    if info["untested"] and not info["priority_gap"]:
        parts.append("<p>仍有需求点未测。下一轮应先补这些条目，再做引申项。</p>")
    if info["priority_gap"]:
        parts.append(
            "<p>需求正文写明的点尚未全部测完，但已经测了引申项。"
            "测试时应优先覆盖需求点，下一轮先补未测的需求点。</p>"
        )
    if info["reqs"]:
        parts.append("<ul>")
        for index, row in enumerate(info["reqs"], start=1):
            # anchors are assigned later in document order; use id-based anchor consistently
            anchor = case_anchor(row, index)
            heading = case_heading(row, index)
            note = row["result"]
            marks = []
            if row.get("requirement_mismatch"):
                marks.append("与需求不符")
            if is_confirm_alias(row.get("raw_result") or ""):
                marks.append("原结果：确认，已计入通过")
            extra = f"（{'；'.join(marks)}）" if marks else ""
            parts.append(
                f'<li><a href="#{html.escape(anchor)}">{html.escape(heading)}</a>'
                f' — {html.escape(note)}{html.escape(extra)}</li>'
            )
        parts.append("</ul>")
    parts.append("</section>")
    return parts


def render_report(
    rows: list[dict],
    meta: dict,
    root: Path,
    skipped: int,
    bug_html: Path | None,
    bug_md: Path | None,
    generated_at: datetime,
    stamp_fallback: datetime,
) -> str:
    title = report_title(meta, stamp_fallback)
    counts = result_counts(rows)
    notes: list[str] = []
    groups = grouped_rows(rows)
    numbered = []
    index = 0
    for _name, group in groups:
        for row in group:
            index += 1
            numbered.append((index, row))
            row["_anchor_index"] = index

    parts = html_head(title)
    if meta.get("sample"):
        parts.append('<p class="banner">本页是报告版式样例，数据已经脱敏，不是一次真实测试的结论。</p>')
    parts.append(f"<h1>{html.escape(title)}</h1>")

    env_line = []
    if meta.get("env"):
        env_line.append(meta["env"])
    if meta.get("side"):
        env_line.append(meta["side"])
    if meta.get("machine"):
        env_line.append(f"机器：{meta['machine']}")
    when = format_shanghai(meta.get("time") or "", stamp_fallback)
    parts.append(f'<p class="meta">测试时间：{html.escape(when)}</p>')
    if env_line:
        parts.append(f'<p class="meta">环境：{html.escape("；".join(env_line))}</p>')

    conclusion = (meta.get("conclusion") or "").strip() or "缺人口一句话结论，待补。"
    parts.append('<section class="conclusion">')
    parts.append(f"<p><strong>结论：</strong>{html.escape(conclusion)}</p>")
    folded = confirm_count(rows)
    badge_bits = []
    for name in RESULT_ORDER:
        if not counts.get(name):
            continue
        extra = f"（含确认 {folded}）" if name == "通过" and folded else ""
        badge_bits.append(badge(name, counts[name], extra))
    for name, number in counts.items():
        if name not in RESULT_ORDER:
            badge_bits.append(badge(name, number))
    parts.append('<div class="badges">')
    parts.extend(badge_bits)
    parts.append("</div>")
    if folded:
        parts.append(f"<p>其中 {folded} 条原结果为「确认」，已计入通过。「已跑待确认」和「部分确认」不合并进通过。</p>")
    parts.append("</section>")
    parts.extend(render_coverage(rows, meta))

    if bug_html is not None:
        md_link = ""
        if bug_md is not None:
            md_link = (
                f'（同目录还有 <a href="{html.escape(bug_md.name)}">{html.escape(bug_md.name)}</a>，方便转发）'
            )
        parts.append(
            '<p class="linkbox"><strong>本批缺陷文档：</strong>'
            f'<a href="{html.escape(bug_html.name)}">{html.escape(bug_html.name)}</a>'
            f"{md_link}。与需求不符的缺陷排在前面。阻塞和已跑待确认列在下方对应分组，不单独装订进缺陷文档。</p>"
        )

    parts.append('<nav class="toc"><h2>目录</h2><ol>')
    for index, row in numbered:
        anchor = case_anchor(row, row.get("_anchor_index") or index)
        heading = case_heading(row, index)
        parts.append(f'<li><a href="#{html.escape(anchor)}">{html.escape(heading)}</a> ' + " ".join(case_tags(row)) + "</li>")
    parts.append("</ol></nav>")

    filter_names = ["all"] + [name for name, _ in groups]
    labels = {"all": "全部"}
    parts.append('<div class="filters" hidden>')
    for name in filter_names:
        label = labels.get(name, name)
        count = len(rows) if name == "all" else next(len(group) for group_name, group in groups if group_name == name)
        pressed = "true" if name == "all" else "false"
        parts.append(
            f'<button type="button" data-filter="{html.escape(name)}" aria-pressed="{pressed}">'
            f"{html.escape(label)} {count}</button>"
        )
    parts.append("</div>")

    cursor = 0
    for group_name, group in groups:
        gid = f"group-{group_name}"
        parts.append(f'<section class="group" id="{html.escape(gid)}">')
        if group_name == "通过" and confirm_count(group):
            heading_name = f"通过（{len(group)}，含确认 {confirm_count(group)}）"
        else:
            heading_name = f"{group_name}（{len(group)}）"
        parts.append(f"<h2>{html.escape(heading_name)}</h2>")
        for row in group:
            cursor += 1
            anchor = case_anchor(row, row.get("_anchor_index") or cursor)
            heading = case_heading(row, cursor)
            classes = "case mismatch" if row.get("requirement_mismatch") else "case"
            parts.append(
                f'<article class="{classes}" id="{html.escape(anchor)}" data-result="{html.escape(group_name)}">'
            )
            parts.append('<div class="case-head">')
            parts.append(f"<h3>{html.escape(heading)}</h3>")
            parts.extend(case_tags(row))
            parts.append("</div>")
            if row.get("requirement_label"):
                parts.append(f'<p class="meta">需求点：{html.escape(row["requirement_label"])}</p>')
            if row.get("summary"):
                parts.append(render_prose(row["summary"], missing=False))
            else:
                parts.append(render_prose(""))
            for shot_index, shot in enumerate(row["shots"], start=1):
                parts.append(render_shot_figure(root, shot, f"{anchor}-{shot_index}", notes, heading))
            parts.append("</article>")
        parts.append("</section>")

    if skipped:
        notes.append(f"跳过 {skipped} 行无法解析的内容")
    if notes:
        parts.append('<section class="notes"><h2>生成时跳过的项</h2><ul>')
        parts.extend(f"<li>{html.escape(note)}</li>" for note in notes)
        parts.append("</ul></section>")

    generated = format_shanghai("", generated_at)
    parts.append(
        f'<p class="footer">报告生成于 {html.escape(generated)}。图片已嵌进本文件，无外链。'
        "密码、验证码和 token 已写成 ***。本文件不包含 secrets 或 leases 目录内容。</p>"
    )
    parts.append("</div>")
    parts.extend(shot_dialog_html())
    parts.append("</body></html>")
    return "\n".join(parts) + "\n"


def resolve_output(output: str | None, root: Path, meta: dict, stamp_fallback: datetime) -> tuple[Path, dict]:
    names = default_filenames(meta, stamp_fallback)
    if not output:
        return root / names["report"], names
    dest = Path(output)
    if output.endswith(("/", "\\")) or dest.is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        return dest / names["report"], names
    return dest, filenames_for_report(dest, meta, stamp_fallback)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="把 results.jsonl 收成给人看的、自带原图的 HTML 报告。")
    parser.add_argument("results", nargs="?", help="默认是当前目录的 results.jsonl")
    parser.add_argument("-o", "--output", help="指定报告路径或目录；未指定时按「简称-时间-report.html」自动起名")
    parser.add_argument("--project", help="项目名，覆盖 jsonl 里的元数据")
    parser.add_argument("--batch", help="批次名，覆盖 jsonl 里的元数据")
    parser.add_argument("--slug", help="需求或批次简称，用于文件名")
    parser.add_argument("--env", help="环境，覆盖 jsonl 里的元数据")
    parser.add_argument("--time", help="测试时间，覆盖 jsonl 里的元数据")
    parser.add_argument("--conclusion", help="人口一句话结论，覆盖 jsonl 里的元数据")
    parser.add_argument("--machine", help="机器，覆盖 jsonl 里的元数据")
    parser.add_argument("--no-bugs", action="store_true", help="只出正报告，不生成或删除缺陷文档")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    source = Path(args.results) if args.results else Path.cwd() / "results.jsonl"
    if forbidden(source) or not source.is_file():
        print(f"html_report: 找不到可用的结果文件 {source}", file=sys.stderr)
        print("用法: python3 html_report.py [results.jsonl] [-o 报告路径或目录]", file=sys.stderr)
        return 2
    root = source.parent.resolve()

    meta, rows, skipped = load_document(source)
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
        print("html_report: results.jsonl 里没有可用记录", file=sys.stderr)
        return 2

    generated_at = datetime.now(tz=SHANGHAI)
    stamp_fallback = generated_at
    if not (meta.get("time") or "").strip():
        try:
            stamp_fallback = datetime.fromtimestamp(source.stat().st_mtime, tz=SHANGHAI)
        except OSError:
            pass

    dest, names = resolve_output(args.output, root, meta, stamp_fallback)
    if forbidden(dest):
        print("html_report: 不把报告写进 secrets 或 leases", file=sys.stderr)
        return 2

    dest.parent.mkdir(parents=True, exist_ok=True)
    bug_html = None
    bug_md = None
    if not args.no_bugs:
        written = write_bug_docs(rows, meta, root, dest.parent, generated_at, names)
        if written:
            bug_html, bug_md = written
            print(f"bugs: {bug_html}")
            print(f"bugs_md: {bug_md}")
        else:
            removed = clear_bug_docs(dest.parent, names)
            for path in removed:
                print(f"bugs_cleared: {path}")

    document = render_report(rows, meta, root, skipped, bug_html, bug_md, generated_at, stamp_fallback)
    dest.write_text(document, encoding="utf-8")
    print(f"report: {dest}")
    print(count_text(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
