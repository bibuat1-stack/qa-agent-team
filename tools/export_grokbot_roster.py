#!/usr/bin/env python3
"""从云电脑只读导出技能、机器人职责模板和例程原文。

只读来源目录，不修改云电脑上的 agents、workflows 或例程。
写入仓库的文本把机器人 id、技能 id 换成名字占位符。
真实 id 映射写到仓库外面的 --id-map，拒绝写进 Git 工作区。

云电脑上的典型用法：

    python3 tools/export_grokbot_roster.py \\
        --agents /home/box/agent-data/agents \\
        --workflows /home/box/agent-data/workflows \\
        --routines /path/to/routine-markdown \\
        --dest /workspace/qa/repo/grokbot \\
        --id-map /workspace/qa/private/id-map.yaml \\
        --exported-at 2026-11-10T20:38:00+08:00

例程存在服务端、磁盘上没有原文时，可以不传 --routines。
这时不覆盖已入库的例程，只提示「待各机器人自报」。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXPORTED_NOTE = "2026-11-10"
PLACEHOLDER_SECRET = "见本地配置"
SKILL_ID_RE = re.compile(r"skill-\d{6,}")
UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)
# 按技能正文里的稳定名决定目录。数字 slug 不写进仓库。
NAME_FOLDER = {
    "项目机器人协作与故障闭环": "project-bot-collab",
}
SETTINGS_KEEP = ("notifyOnAgentUpdates",)
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yml", ".yaml", ".py", ".sh"}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s\-]?)?1[3-9]\d{9}(?!\d)")
INTL_PHONE_RE = re.compile(r"(?<!\w)\+\d{10,15}(?!\d)")
WEBHOOK_RE = re.compile(
    r"https?://[^\s)\"'`<>]*(?:webhook|hooks\.slack\.com|discord(?:app)?\.com/api/webhooks)[^\s)\"'`<>]*",
    re.IGNORECASE,
)
KEY_RES = (
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_\-]{20,}")),
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_token", re.compile(r"(?:ghp|github_pat)_[A-Za-z0-9_]{16,}")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9\-]+")),
    ("bearer", re.compile(r"Bearer\s+[A-Za-z0-9._\-]{12,}")),
    ("notion_token", re.compile(r"(?:secret_|ntn_)[A-Za-z0-9]{10,}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}")),
)
ASSIGN_RE = re.compile(
    r"(?i)\b(password|passwd|pwd|api[_-]?key|secret|token|cookie)\b(\s*[:=]\s*)(['\"])([^'\"]{6,})(['\"])"
)


def yaml_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def inside_git_worktree(path: Path) -> bool:
    for parent in [path, *path.parents]:
        if (parent / ".git").exists():
            return True
    return False


def safe_segment(name: str) -> str:
    cleaned = name.replace("/", "／").replace("\\", "＼").replace("\x00", "").strip()
    if cleaned in ("", ".", ".."):
        raise SystemExit(f"无法作为文件名: {name!r}")
    return cleaned


def skill_version(text: str) -> str:
    match = re.search(r"版本[:：]\s*(v?\d+(?:\.\d+)*)", text)
    return match.group(1) if match else ""


def skill_front_name(text: str, folder: str) -> str:
    match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
    if not match:
        return folder
    return match.group(1).strip().strip("'\"")


def load_agents(agents_dir: Path) -> list[dict]:
    bots = []
    for path in sorted(p for p in agents_dir.iterdir() if p.is_dir()):
        profile_path = path / "profile.json"
        settings_path = path / "settings.json"
        if not profile_path.is_file():
            continue
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        settings = {}
        if settings_path.is_file():
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        name = str(profile.get("name") or "").strip()
        if not name:
            raise SystemExit(f"{path.name} 的 profile 没有 name")
        kept = {key: settings[key] for key in SETTINGS_KEEP if key in settings}
        bots.append(
            {
                "agent_id": path.name,
                "name": name,
                "title": str(profile.get("title") or ""),
                "description": str(profile.get("description") or ""),
                "server_id": str(profile.get("serverId") or ""),
                "settings": kept,
                "dropped_settings": sorted(set(settings) - set(SETTINGS_KEEP)),
            }
        )
    names = [bot["name"] for bot in bots]
    if len(names) != len(set(names)):
        raise SystemExit("机器人 name 有重名，停止导出")
    return bots


def load_skills(workflows_dir: Path) -> list[dict]:
    skills = []
    for path in sorted(p for p in workflows_dir.iterdir() if p.is_dir()):
        skill_md = path / "SKILL.md"
        if not skill_md.is_file():
            continue
        text = skill_md.read_text(encoding="utf-8")
        name = skill_front_name(text, path.name)
        if name in NAME_FOLDER:
            dest = NAME_FOLDER[name]
        elif SKILL_ID_RE.fullmatch(path.name):
            dest = safe_segment(name)
        else:
            dest = path.name
        skills.append(
            {
                "source_slug": path.name,
                "name": name,
                "folder": dest,
                "version": skill_version(text),
                "root": path,
            }
        )
    folders = [item["folder"] for item in skills]
    if len(folders) != len(set(folders)):
        raise SystemExit("技能目标目录重名，停止导出")
    return skills


class Rewriter:
    def __init__(self, bots: list[dict], skills: list[dict]):
        self.bot_ids = {bot["agent_id"].lower(): bot["name"] for bot in bots}
        self.skill_ids = {
            item["source_slug"]: item["name"]
            for item in skills
            if SKILL_ID_RE.fullmatch(item["source_slug"])
        }
        self.server_ids = {bot["server_id"] for bot in bots if bot["server_id"]}
        self.hits: list[tuple[str, str]] = []

    def note(self, label: str, path: Path) -> None:
        self.hits.append((label, str(path)))

    def apply(self, text: str, path: Path) -> str:
        def bot_sub(match: re.Match[str]) -> str:
            name = self.bot_ids.get(match.group(0).lower())
            if not name:
                return match.group(0)
            self.note("bot_id", path)
            return "{{bot:" + name + "}}"

        def skill_sub(match: re.Match[str]) -> str:
            slug = match.group(0)
            name = self.skill_ids.get(slug)
            self.note("skill_id" if name else "unknown_skill_id", path)
            if not name:
                return "{{skill:未登记}}"
            return "{{skill:" + name + "}}"

        text = UUID_RE.sub(bot_sub, text)
        text = SKILL_ID_RE.sub(skill_sub, text)
        text = self.redact(text, path)
        return text

    def redact(self, text: str, path: Path) -> str:
        def swap(pattern: re.Pattern[str], label: str, replacement: str, current: str) -> str:
            def repl(match: re.Match[str]) -> str:
                self.note(label, path)
                return replacement

            return pattern.sub(repl, current)

        for label, pattern in KEY_RES:
            text = swap(pattern, label, PLACEHOLDER_SECRET, text)
        text = swap(WEBHOOK_RE, "webhook", PLACEHOLDER_SECRET, text)

        def email_repl(match: re.Match[str]) -> str:
            addr = match.group(0)
            if addr.lower().endswith(("@example.com", "@example.org")):
                self.note("example_email_kept", path)
                return addr
            self.note("email", path)
            return PLACEHOLDER_SECRET

        text = EMAIL_RE.sub(email_repl, text)
        text = swap(PHONE_RE, "phone", PLACEHOLDER_SECRET, text)
        text = swap(INTL_PHONE_RE, "phone", PLACEHOLDER_SECRET, text)

        def assign_repl(match: re.Match[str]) -> str:
            value = match.group(4)
            if value.startswith(("/", ".", "$", "{")) or "见本地配置" in value:
                return match.group(0)
            self.note("assigned_secret", path)
            return match.group(1) + match.group(2) + match.group(3) + PLACEHOLDER_SECRET + match.group(5)

        text = ASSIGN_RE.sub(assign_repl, text)

        def person_star(match: re.Match[str]) -> str:
            self.note("person_name", path)
            return PLACEHOLDER_SECRET

        text = re.sub(r"(?i)sean\s*\*", person_star, text)

        def person_word(match: re.Match[str]) -> str:
            self.note("person_name", path)
            return "用户"

        text = re.sub(r"(?i)sean", person_word, text)
        text = re.sub(r"(?i)vico", person_star, text)

        for server_id in self.server_ids:
            pattern = re.compile(rf"(?<!\d){re.escape(server_id)}(?!\d)")
            text = swap(pattern, "server_id", PLACEHOLDER_SECRET, text)
        return text


def write_bots(dest: Path, bots: list[dict], rewriter: Rewriter, exported_at: str) -> None:
    bots_dir = dest / "bots"
    bots_dir.mkdir(parents=True, exist_ok=True)
    for bot in bots:
        body = rewriter.apply(bot["description"], Path(f"bots/{bot['name']}.md"))
        title = bot["title"]
        notify = bot["settings"].get("notifyOnAgentUpdates")
        lines = [
            "---",
            f"stable_name: {yaml_str(bot['name'])}",
            f"title: {yaml_str(title)}",
        ]
        if isinstance(notify, bool):
            lines.append(f"notify_on_agent_updates: {'true' if notify else 'false'}")
        lines.extend(
            [
                f"exported_at: {yaml_str(exported_at)}",
                "---",
                "",
                f"# {bot['name']}",
                "",
                body.rstrip() + "\n",
            ]
        )
        (bots_dir / f"{safe_segment(bot['name'])}.md").write_text("\n".join(lines), encoding="utf-8")


def write_skills(dest: Path, skills: list[dict], rewriter: Rewriter) -> None:
    skills_dir = dest / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    for skill in skills:
        target = skills_dir / skill["folder"]
        target.mkdir(parents=True, exist_ok=True)
        for source in sorted(p for p in skill["root"].rglob("*") if p.is_file()):
            relative = source.relative_to(skill["root"])
            out = target / relative
            out.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix.lower() not in TEXT_SUFFIXES:
                raise SystemExit(f"遇到非文本技能文件，停止: {source}")
            text = rewriter.apply(source.read_text(encoding="utf-8"), Path("skills") / skill["folder"] / relative)
            out.write_text(text, encoding="utf-8")


def write_routines(dest: Path, routines_dir: Path | None, rewriter: Rewriter) -> None:
    target = dest / "routines"
    target.mkdir(parents=True, exist_ok=True)
    if routines_dir is None:
        readme = target / "README.md"
        if not readme.exists():
            readme.write_text("# 例程原文\n\n其他机器人例程：待各机器人自报。\n", encoding="utf-8")
        print("未提供 --routines，不覆盖已有例程。其他机器人例程：待各机器人自报。", file=sys.stderr)
        return
    for source in sorted(p for p in routines_dir.iterdir() if p.is_file()):
        if source.suffix.lower() not in TEXT_SUFFIXES:
            raise SystemExit(f"遇到非文本例程文件，停止: {source}")
        text = rewriter.apply(source.read_text(encoding="utf-8"), Path("routines") / source.name)
        if source.name == "README.md" and "待各机器人自报" not in text:
            text = text.rstrip() + "\n\n其他机器人例程：待各机器人自报。\n"
        (target / source.name).write_text(text, encoding="utf-8")


def write_example(dest: Path, bots: list[dict], skills: list[dict]) -> None:
    mapping = dest / "mapping"
    mapping.mkdir(parents=True, exist_ok=True)
    lines = [
        "version: 1",
        "note: 真实 id 只放 Drive 上的 id-map.yaml，不进 Git。下面的账号槽故意留空。",
        "bots:",
    ]
    for bot in bots:
        lines.extend(
            [
                f"  - stable_name: {yaml_str(bot['name'])}",
                f"    template: {yaml_str('bots/' + safe_segment(bot['name']) + '.md')}",
                "    accounts:",
                "      A: {agent_id: \"\"}",
                "      B: {agent_id: \"\"}",
            ]
        )
    lines.append("skills:")
    for skill in skills:
        lines.extend(
            [
                f"  - stable_name: {yaml_str(skill['name'])}",
                f"    folder: {yaml_str(skill['folder'])}",
                f"    version: {yaml_str(skill['version'])}",
                "    accounts:",
                "      A: {slug: \"\"}",
                "      B: {slug: \"\"}",
            ]
        )
    lines.extend(
        [
            "routines:",
            "  - note: 已入库的只有总控例程。其他机器人例程：待各机器人自报。",
            "",
        ]
    )
    (mapping / "id-map.example.yaml").write_text("\n".join(lines), encoding="utf-8")


def write_id_map(path: Path, bots: list[dict], skills: list[dict], exported_at: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "version: 1",
        f"exported_at: {yaml_str(exported_at)}",
        "note: 这个文件含真实 id，不要放进 Git 或聊天。",
        "bots:",
    ]
    for bot in bots:
        lines.extend(
            [
                f"  - stable_name: {yaml_str(bot['name'])}",
                f"    agent_id: {yaml_str(bot['agent_id'])}",
                f"    server_id: {yaml_str(bot['server_id'])}",
            ]
        )
    lines.append("skills:")
    for skill in skills:
        lines.extend(
            [
                f"  - stable_name: {yaml_str(skill['name'])}",
                f"    folder: {yaml_str(skill['folder'])}",
                f"    source_slug: {yaml_str(skill['source_slug'])}",
                f"    version: {yaml_str(skill['version'])}",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def scan_dest(dest: Path, rewriter: Rewriter) -> list[str]:
    problems = []
    for path in sorted(p for p in dest.rglob("*") if p.is_file()):
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "id-map.example.yaml":
            continue
        text = path.read_text(encoding="utf-8")
        for match in UUID_RE.finditer(text):
            if match.group(0).lower() in rewriter.bot_ids:
                problems.append(f"仍含机器人 id: {path}")
                break
        if SKILL_ID_RE.search(text):
            problems.append(f"仍含技能数字 id: {path}")
        for _label, pattern in KEY_RES:
            if pattern.search(text):
                problems.append(f"仍含密钥样式: {path}")
                break
        if WEBHOOK_RE.search(text):
            problems.append(f"仍含 webhook: {path}")
        for match in EMAIL_RE.finditer(text):
            if not match.group(0).lower().endswith(("@example.com", "@example.org")):
                problems.append(f"仍含邮箱: {path}")
                break
        if PHONE_RE.search(text) or INTL_PHONE_RE.search(text):
            problems.append(f"仍含手机号: {path}")
        if re.search(r"(?i)sean|vico", text):
            problems.append(f"仍含已要求去掉的人名: {path}")
    return problems


def summarize(rewriter: Rewriter) -> None:
    counts: dict[str, int] = {}
    files: dict[str, set[str]] = {}
    for label, path in rewriter.hits:
        counts[label] = counts.get(label, 0) + 1
        files.setdefault(label, set()).add(path)
    print("去密与占位统计（只报类别和次数，不打印原文）:")
    for label in sorted(counts):
        print(f"  {label}: {counts[label]} 处，{len(files[label])} 个文件")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="只读导出 Grok Bot 技能、职责模板和例程原文")
    parser.add_argument("--agents", type=Path, required=True)
    parser.add_argument("--workflows", type=Path, required=True)
    parser.add_argument("--routines", type=Path, default=None)
    parser.add_argument("--dest", type=Path, required=True, help="通常是仓库里的 grokbot 目录")
    parser.add_argument("--id-map", type=Path, required=True, help="真实映射的输出路径，必须在 Git 工作区之外")
    parser.add_argument("--exported-at", default=EXPORTED_NOTE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agents_dir = args.agents.resolve()
    workflows_dir = args.workflows.resolve()
    dest = args.dest.resolve()
    id_map = args.id_map.resolve()
    routines = args.routines.resolve() if args.routines else None
    for label, path in ("agents", agents_dir), ("workflows", workflows_dir):
        if not path.is_dir():
            print(f"{label} 目录不存在: {path}", file=sys.stderr)
            return 2
    if routines is not None and not routines.is_dir():
        print(f"routines 目录不存在: {routines}", file=sys.stderr)
        return 2
    if inside_git_worktree(id_map):
        print("拒绝把真实 id 映射写进 Git 工作区。请把 --id-map 指到仓库外，例如 Drive 同步目录。", file=sys.stderr)
        return 2
    if dest in id_map.parents:
        print("拒绝把真实 id 映射写进导出目录。", file=sys.stderr)
        return 2

    bots = load_agents(agents_dir)
    skills = load_skills(workflows_dir)
    rewriter = Rewriter(bots, skills)
    write_bots(dest, bots, rewriter, args.exported_at)
    write_skills(dest, skills, rewriter)
    write_routines(dest, routines, rewriter)
    write_example(dest, bots, skills)
    write_id_map(id_map, bots, skills, args.exported_at)

    dropped = sorted({key for bot in bots for key in bot["dropped_settings"]})
    if dropped:
        print("settings.json 中未写入仓库的字段: " + ", ".join(dropped), file=sys.stderr)

    problems = scan_dest(dest, rewriter)
    summarize(rewriter)
    print(f"机器人 {len(bots)}，技能 {len(skills)}，真实映射已写到仓库外。")
    if problems:
        print("导出后检查未通过:", file=sys.stderr)
        for item in problems:
            print("  " + item, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
