"""bootstrap 在工具链没变时跳过 pip 和浏览器下载。使用本地 git，不访问 GitHub。"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "bootstrap_bot_computer.sh"


def _git(origin: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(origin), *args], check=True, capture_output=True, text=True)


def _bootstrap(origin: Path, qa_root: Path, venv: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "QA_ROOT": str(qa_root),
            "VENV": str(venv),
            "QA_SKIP_REAP": "1",
            "QA_INSTALL_GH": "0",
        }
    )
    return subprocess.run(
        ["bash", str(SCRIPT), origin.as_uri(), "main"],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_second_run_reuses_toolchain_and_prunes_old_runs(tmp_path: Path) -> None:
    origin = tmp_path / "origin"
    origin.mkdir()
    _git(origin, "init", "-b", "main")
    _git(origin, "config", "user.email", "bootstrap-test@example.com")
    _git(origin, "config", "user.name", "bootstrap-test")
    (origin / "requirements.txt").write_text("# no third-party packages\n", encoding="utf-8")
    _git(origin, "add", "requirements.txt")
    _git(origin, "commit", "-m", "init")

    qa_root = tmp_path / "qa"
    venv = tmp_path / "venv"
    first = _bootstrap(origin, qa_root, venv)
    assert first.returncode == 0, first.stderr + first.stdout
    assert "toolchain=installed" in first.stdout
    assert (qa_root / "cloud.env").read_text(encoding="utf-8").startswith("QA_CLOUD=1\n")

    runs = qa_root / "runs"
    old = runs / "20000101-010101"
    recent = runs / "20990101-010101"
    kept = runs / "notes"
    old.mkdir()
    recent.mkdir()
    kept.mkdir()
    subprocess.run(["touch", "-d", "10 days ago", str(old), str(kept)], check=True)

    second = _bootstrap(origin, qa_root, venv)
    assert second.returncode == 0, second.stderr + second.stdout
    assert "toolchain=cached" in second.stdout
    assert not old.exists()
    assert recent.exists()
    assert kept.exists()

    (origin / "requirements.txt").write_text("# no third-party packages\n# changed\n", encoding="utf-8")
    _git(origin, "add", "requirements.txt")
    _git(origin, "commit", "-m", "change requirements")
    third = _bootstrap(origin, qa_root, venv)
    assert third.returncode == 0, third.stderr + third.stdout
    assert "toolchain=installed" in third.stdout
