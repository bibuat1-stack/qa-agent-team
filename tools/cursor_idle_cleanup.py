#!/usr/bin/env python3
"""清理 Cursor 云端本机上已确认作废的临时工作区。

只处理 /tmp/cursor-idle-workspaces 的直接子目录。子目录同时满足下面四条才删除：

- 里面有 IDLE_OK.json，且 disposable 为 true、reason 为 task-finished
- 目录本身不是符号链接，解析后仍在扫描根里面
- 没有任何进程把它当作工作目录、打开其中的文件，或在参数里写了它的绝对路径
- 里面没有凭证、登录态、报告、日志或 git 目录

不结束进程，也不按占用高低、存在时长或对话是否打开来判断。
扫不到标记的目录保持不动，也不因此发通知。
默认只检查。加上 --apply 才删除。本脚本不安装调度，也不碰 /workspace/qa。
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path

MARKER = "IDLE_OK.json"
ROOT_NAME = "cursor-idle-workspaces"
DEFAULT_ROOT = Path("/tmp") / ROOT_NAME
MAX_MARKER_BYTES = 4096
MAX_ENTRIES = 5000
SENSITIVE_DIRS = {"reports", "logs", "secrets", "leases", ".ssh", ".git"}
SENSITIVE_FILES = {".env", "id_rsa", "credentials.json", "cookies.sqlite", "cookies.txt"}
SENSITIVE_SUFFIXES = (".pem", ".key")


def _relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def validate_scan_root(root: Path) -> str | None:
    """返回拒绝原因。扫描根还不存在时返回 None，调用方按空跑处理。"""
    if root.is_symlink():
        return "扫描根是符号链接"
    resolved = root.resolve() if root.exists() else root.absolute()
    if resolved.name != ROOT_NAME:
        return "扫描根目录名必须是 cursor-idle-workspaces"
    tmp = Path("/tmp").resolve()
    if resolved == tmp or not _relative_to(resolved, tmp):
        return "扫描根必须在 /tmp 下"
    qa = Path("/workspace/qa")
    qa_resolved = qa.resolve() if qa.exists() else qa
    if resolved == qa_resolved or _relative_to(resolved, qa_resolved):
        return "不清理 Grok Bot 云电脑目录"
    if root.exists() and not root.is_dir():
        return "扫描根不是目录"
    return None


def _read_link(path: Path) -> str:
    try:
        return os.readlink(path)
    except OSError:
        return ""


def _under(path: Path, parent: Path) -> bool:
    if path == parent or _relative_to(path, parent):
        return True
    return False


def directory_in_use(directory: Path, proc_root: Path) -> bool:
    """进程把该目录当工作目录、打开了里面的文件，或参数里写了它的绝对路径。"""
    if not proc_root.is_dir():
        return True
    target = directory.resolve()
    self_pid = str(os.getpid())
    try:
        pid_dirs = list(proc_root.iterdir())
    except OSError:
        return True
    for pid_dir in pid_dirs:
        if not pid_dir.name.isdigit() or pid_dir.name == self_pid:
            continue
        seen: list[Path] = []
        cwd = _read_link(pid_dir / "cwd")
        if cwd:
            seen.append(Path(cwd))
        fd_dir = pid_dir / "fd"
        if fd_dir.is_dir():
            try:
                fd_names = list(fd_dir.iterdir())
            except OSError:
                fd_names = []
            for fd in fd_names:
                link = _read_link(fd)
                if link:
                    seen.append(Path(link))
        cmdline = []
        try:
            cmdline = (pid_dir / "cmdline").read_bytes().split(b"\0")
        except OSError:
            cmdline = []
        for raw in cmdline:
            if raw.startswith(b"/"):
                seen.append(Path(os.fsdecode(raw)))
        for candidate in seen:
            try:
                resolved = candidate.resolve()
            except OSError:
                continue
            if _under(resolved, target):
                return True
    return False


def _sensitive_reason(directory: Path) -> str | None:
    seen = 0
    for current, dirs, files in os.walk(directory, followlinks=False):
        current_path = Path(current)
        if current_path.is_symlink():
            return "含指向外部的符号链接"
        for name in list(dirs):
            seen += 1
            if seen > MAX_ENTRIES:
                return "目录条目过多，未删除"
            child = current_path / name
            if child.is_symlink():
                return "含符号链接"
            if name in SENSITIVE_DIRS:
                return "含报告、日志、凭证或 git 目录"
        for name in files:
            seen += 1
            if seen > MAX_ENTRIES:
                return "目录条目过多，未删除"
            child = current_path / name
            if child.is_symlink() and name != MARKER:
                return "含符号链接"
            if name == ".env" or name.startswith(".env.") or name in SENSITIVE_FILES or name.endswith(SENSITIVE_SUFFIXES):
                return "含凭证或登录态文件"
    return None


def _marker_reason(directory: Path) -> tuple[bool, str | None]:
    """返回 (可删除, 需要人决定的原因)。两者都空表示没有作废标记，保持不动。"""
    marker = directory / MARKER
    if not marker.exists() and not marker.is_symlink():
        return False, None
    if marker.is_symlink():
        return False, "作废标记是符号链接"
    try:
        info = marker.lstat()
    except OSError:
        return False, "作废标记无法读取"
    if not stat.S_ISREG(info.st_mode):
        return False, "作废标记不是普通文件"
    if info.st_size > MAX_MARKER_BYTES:
        return False, "作废标记过大"
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return False, "作废标记无法解析"
    if not isinstance(payload, dict):
        return False, "作废标记格式不对"
    if payload.get("disposable") is True and payload.get("reason") == "task-finished":
        return True, None
    return False, "作废标记未确认任务已结束"


def classify(directory: Path, proc_root: Path) -> str | None:
    """返回需要人决定的原因。返回 None 表示可以删除。调用前须已确认目录在扫描根内。"""
    if directory.is_symlink():
        return "是符号链接"
    confirmed, marker_problem = _marker_reason(directory)
    if marker_problem:
        return marker_problem
    if not confirmed:
        return None
    sensitive = _sensitive_reason(directory)
    if sensitive:
        return sensitive
    if not proc_root.is_dir():
        return "读不到进程表，未删除"
    if directory_in_use(directory, proc_root):
        return ""
    return None


def inspect_root(root: Path, proc_root: Path) -> dict:
    deleted_ready: list[str] = []
    kept_in_use: list[str] = []
    needs_decision: list[dict[str, str]] = []
    skipped = 0
    if not root.exists():
        return {
            "ready": deleted_ready,
            "kept_in_use": kept_in_use,
            "needs_decision": needs_decision,
            "skipped_unconfirmed": skipped,
            "root_exists": False,
        }
    root_resolved = root.resolve()
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if child.name.startswith("."):
            needs_decision.append({"name": child.name, "reason": "隐藏条目不自动删除"})
            continue
        if child.is_symlink() or not child.is_dir():
            if child.is_symlink() or child.exists():
                needs_decision.append({"name": child.name, "reason": "不是普通目录"})
            continue
        try:
            resolved = child.resolve()
        except OSError:
            needs_decision.append({"name": child.name, "reason": "路径无法解析"})
            continue
        if resolved.parent != root_resolved:
            needs_decision.append({"name": child.name, "reason": "解析后不在扫描根内"})
            continue
        confirmed, marker_problem = _marker_reason(child)
        if marker_problem:
            needs_decision.append({"name": child.name, "reason": marker_problem})
            continue
        if not confirmed:
            skipped += 1
            continue
        problem = classify(child, proc_root)
        if problem is None:
            deleted_ready.append(child.name)
            continue
        if problem == "":
            kept_in_use.append(child.name)
            continue
        needs_decision.append({"name": child.name, "reason": problem})
    return {
        "ready": deleted_ready,
        "kept_in_use": kept_in_use,
        "needs_decision": needs_decision,
        "skipped_unconfirmed": skipped,
        "root_exists": True,
    }


def run_cleanup(root: Path, apply: bool, proc_root: Path | None = None) -> dict:
    proc = proc_root or Path("/proc")
    refusal = validate_scan_root(root)
    if refusal:
        return {
            "scope": "cursor-cloud-vm",
            "scan_root": str(root),
            "apply": apply,
            "refused": refusal,
            "deleted": [],
            "kept_in_use": [],
            "needs_decision": [],
            "skipped_unconfirmed": 0,
            "notify": True,
        }
    found = inspect_root(root, proc)
    deleted: list[str] = []
    if apply and found["root_exists"]:
        for name in found["ready"]:
            target = root / name
            if target.is_symlink() or not target.is_dir():
                found["needs_decision"].append({"name": name, "reason": "删除前状态变了"})
                continue
            if target.resolve().parent != root.resolve():
                found["needs_decision"].append({"name": name, "reason": "删除前路径变了"})
                continue
            if directory_in_use(target, proc):
                found["kept_in_use"].append(name)
                continue
            _remove_tree(target)
            if target.exists():
                found["needs_decision"].append({"name": name, "reason": "删除没有完成"})
            else:
                deleted.append(name)
    elif not apply:
        deleted = []
    notify = bool(deleted or found["needs_decision"])
    return {
        "scope": "cursor-cloud-vm",
        "scan_root": str(root),
        "apply": apply,
        "root_exists": found["root_exists"],
        "deleted": deleted,
        "would_delete": [] if apply else found["ready"],
        "kept_in_use": found["kept_in_use"],
        "needs_decision": found["needs_decision"],
        "skipped_unconfirmed": found["skipped_unconfirmed"],
        "notify": notify,
    }


def _remove_tree(path: Path) -> None:
    if path.is_symlink():
        return
    for child in list(path.iterdir()):
        if child.is_symlink() or child.is_file():
            child.unlink()
        elif child.is_dir():
            _remove_tree(child)
    path.rmdir()


def exit_code(result: dict) -> int:
    if result.get("refused"):
        return 3
    if result.get("needs_decision"):
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="只删除 Cursor 云端本机上已确认作废且无人占用的临时工作区。")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="扫描根，必须是 /tmp/cursor-idle-workspaces")
    parser.add_argument("--apply", action="store_true", help="真正删除。不加时只检查")
    parser.add_argument("--proc", type=Path, default=Path("/proc"), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    result = run_cleanup(args.root, args.apply, args.proc)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
