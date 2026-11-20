"""Cursor 云端作废工作区清理的本地检查。不访问网络，不结束进程。"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "cursor_idle_cleanup", ROOT / "tools" / "cursor_idle_cleanup.py"
)
cleanup = importlib.util.module_from_spec(SPEC)
sys.modules["cursor_idle_cleanup"] = cleanup
assert SPEC.loader is not None
SPEC.loader.exec_module(cleanup)


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "tmp" / "cursor-idle-workspaces"
    root.mkdir(parents=True)
    return root


def _mark(directory: Path, payload: dict | str | None = None) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    body = {"disposable": True, "reason": "task-finished"} if payload is None else payload
    text = body if isinstance(body, str) else json.dumps(body)
    (directory / "IDLE_OK.json").write_text(text, encoding="utf-8")


def _patch_tmp(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(cleanup, "validate_scan_root", _allow_test_root)


def _proc(tmp_path: Path) -> Path:
    proc = tmp_path / "proc"
    proc.mkdir(exist_ok=True)
    return proc


def _allow_test_root(root: Path) -> str | None:
    resolved = root.resolve() if root.exists() else root.absolute()
    if resolved.name != "cursor-idle-workspaces":
        return "扫描根目录名必须是 cursor-idle-workspaces"
    if root.exists() and not root.is_dir():
        return "扫描根不是目录"
    if root.is_symlink():
        return "扫描根是符号链接"
    return None


def test_apply_removes_only_marked_unused_workspace(tmp_path: Path, monkeypatch) -> None:
    _patch_tmp(monkeypatch, tmp_path)
    root = _root(tmp_path)
    finished = root / "finished-task"
    _mark(finished)
    (finished / "scratch.txt").write_text("done", encoding="utf-8")
    unmarked = root / "still-open"
    unmarked.mkdir()
    (unmarked / "notes.txt").write_text("keep", encoding="utf-8")

    result = cleanup.run_cleanup(root, apply=True, proc_root=_proc(tmp_path))

    assert result["deleted"] == ["finished-task"]
    assert not finished.exists()
    assert (unmarked / "notes.txt").read_text(encoding="utf-8") == "keep"
    assert result["skipped_unconfirmed"] == 1
    assert result["notify"] is True
    assert cleanup.exit_code(result) == 0


def test_dry_run_keeps_marked_workspace(tmp_path: Path, monkeypatch) -> None:
    _patch_tmp(monkeypatch, tmp_path)
    root = _root(tmp_path)
    finished = root / "finished-task"
    _mark(finished)

    result = cleanup.run_cleanup(root, apply=False, proc_root=_proc(tmp_path))

    assert result["would_delete"] == ["finished-task"]
    assert result["deleted"] == []
    assert finished.is_dir()
    assert result["notify"] is False


def test_process_holding_directory_blocks_delete(tmp_path: Path, monkeypatch) -> None:
    _patch_tmp(monkeypatch, tmp_path)
    root = _root(tmp_path)
    held = root / "held-task"
    _mark(held)
    proc_root = _proc(tmp_path)
    pid_dir = proc_root / "4242"
    pid_dir.mkdir(parents=True)
    (pid_dir / "cwd").symlink_to(held)
    (pid_dir / "cmdline").write_bytes(b"sleep\x0030\x00")
    (pid_dir / "fd").mkdir()

    result = cleanup.run_cleanup(root, apply=True, proc_root=proc_root)

    assert held.is_dir()
    assert result["deleted"] == []
    assert result["kept_in_use"] == ["held-task"]
    assert result["notify"] is False


def test_open_file_blocks_delete(tmp_path: Path, monkeypatch) -> None:
    _patch_tmp(monkeypatch, tmp_path)
    root = _root(tmp_path)
    held = root / "held-file"
    _mark(held)
    target = held / "scratch.txt"
    target.write_text("open", encoding="utf-8")
    proc_root = _proc(tmp_path)
    pid_dir = proc_root / "5252"
    fd_dir = pid_dir / "fd"
    fd_dir.mkdir(parents=True)
    (pid_dir / "cwd").symlink_to(tmp_path)
    (pid_dir / "cmdline").write_bytes(b"")
    (fd_dir / "7").symlink_to(target)

    result = cleanup.run_cleanup(root, apply=True, proc_root=proc_root)

    assert target.exists()
    assert result["kept_in_use"] == ["held-file"]


def test_bad_marker_needs_decision_and_keeps_files(tmp_path: Path, monkeypatch) -> None:
    _patch_tmp(monkeypatch, tmp_path)
    root = _root(tmp_path)
    bad = root / "bad-marker"
    _mark(bad, "{")
    (bad / "keep.txt").write_text("stay", encoding="utf-8")

    result = cleanup.run_cleanup(root, apply=True, proc_root=_proc(tmp_path))

    assert (bad / "keep.txt").exists()
    assert result["needs_decision"] == [{"name": "bad-marker", "reason": "作废标记无法解析"}]
    assert cleanup.exit_code(result) == 2


def test_reports_and_env_are_not_deleted(tmp_path: Path, monkeypatch) -> None:
    _patch_tmp(monkeypatch, tmp_path)
    root = _root(tmp_path)
    reported = root / "with-report"
    _mark(reported)
    (reported / "reports").mkdir()
    secret = root / "with-secret"
    _mark(secret)
    (secret / ".env").write_text("TOKEN=nope", encoding="utf-8")

    result = cleanup.run_cleanup(root, apply=True, proc_root=_proc(tmp_path))

    assert reported.is_dir()
    assert secret.is_dir()
    assert (secret / ".env").read_text(encoding="utf-8") == "TOKEN=nope"
    reasons = {item["name"]: item["reason"] for item in result["needs_decision"]}
    assert reasons["with-report"] == "含报告、日志、凭证或 git 目录"
    assert reasons["with-secret"] == "含凭证或登录态文件"


def test_symlink_workspace_is_not_removed(tmp_path: Path, monkeypatch) -> None:
    _patch_tmp(monkeypatch, tmp_path)
    root = _root(tmp_path)
    outside = tmp_path / "outside-repo"
    outside.mkdir()
    (outside / "keep.txt").write_text("stay", encoding="utf-8")
    (root / "linked").symlink_to(outside, target_is_directory=True)

    result = cleanup.run_cleanup(root, apply=True, proc_root=_proc(tmp_path))

    assert (outside / "keep.txt").exists()
    assert result["deleted"] == []
    assert result["needs_decision"][0]["name"] == "linked"


def test_cli_refuses_bot_computer_and_missing_root_is_quiet() -> None:
    refused = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "cursor_idle_cleanup.py"), "--root", "/workspace/qa", "--apply"],
        check=False,
        capture_output=True,
        text=True,
    )
    payload = json.loads(refused.stdout)
    assert refused.returncode == 3
    assert "Grok Bot" in payload["refused"] or "cursor-idle-workspaces" in payload["refused"]

    missing = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "cursor_idle_cleanup.py"),
            "--root",
            "/tmp/cursor-idle-workspaces",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    quiet = json.loads(missing.stdout)
    assert missing.returncode == 0
    assert quiet["deleted"] == []
    assert quiet["notify"] is False
