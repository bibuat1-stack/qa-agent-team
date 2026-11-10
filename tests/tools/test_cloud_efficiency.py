"""云电脑并发规划和运行摘要。不启动浏览器，也不访问被测系统。"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tools.cloud_efficiency import (
    UI_MIN_MB,
    mem_available_mb,
    parse_junit,
    plan_suite,
    redact_message,
    ui_pytest_args,
    worker_count,
    write_run_summary,
)

ROOT = Path(__file__).resolve().parents[2]


def test_mem_available_parses_kib() -> None:
    text = "MemTotal: 8000000 kB\nMemAvailable: 2560000 kB\n"
    assert mem_available_mb(text) == 2500


def test_mem_available_missing() -> None:
    assert mem_available_mb("MemTotal: 1 kB\n") is None


def test_api_workers_follow_memory() -> None:
    assert worker_count("api", mem_mb=500, cpu=8) == 1
    assert worker_count("api", mem_mb=1500, cpu=8) == 2
    assert worker_count("api", mem_mb=4000, cpu=8) == 4
    assert worker_count("api", mem_mb=4000, cpu=2) == 2
    assert worker_count("api", mem_mb=4000, cpu=8, explicit=1) == 1


def test_ui_workers_stay_small() -> None:
    assert worker_count("ui", mem_mb=UI_MIN_MB - 1, cpu=8) == 0
    assert worker_count("ui", mem_mb=1000, cpu=8) == 1
    assert worker_count("ui", mem_mb=4000, cpu=8) == 2


def test_low_memory_blocks_ui_and_keeps_api() -> None:
    blocked = plan_suite(suite="ui", markers="smoke", mem_mb=200, cpu=4, explicit_workers=None, force_ui=False)
    assert blocked.blocked
    assert blocked.workers == 0

    forced = plan_suite(suite="ui", markers=None, mem_mb=200, cpu=4, explicit_workers=None, force_ui=True)
    assert forced.blocked is None
    assert forced.ui_artifacts is True

    downgraded = plan_suite(suite="all", markers=None, mem_mb=200, cpu=4, explicit_workers=None, force_ui=False)
    assert downgraded.suite == "api"
    assert downgraded.ui_artifacts is False
    assert downgraded.note


def test_ui_args_do_not_override_caller() -> None:
    args = ui_pytest_args(["--video", "on", "--output", "custom"], output_dir="reports/playwright")
    assert args.count("--video") == 1
    assert "on" in args
    assert "custom" in args
    assert "--tracing" in args
    assert "retain-on-failure" in args
    assert "only-on-failure" in args


def test_junit_summary_redacts_secrets(tmp_path: Path) -> None:
    xml = """<?xml version="1.0" ?>
    <testsuites>
      <testsuite name="api" tests="3" failures="1" errors="0" skipped="1" time="1.5">
        <testcase classname="tests.api.test_posts" name="test_ok" time="0.2"/>
        <testcase classname="tests.api.test_posts" name="test_skip" time="0.1"><skipped/></testcase>
        <testcase classname="tests.api.test_posts" name="test_bad" time="1.2">
          <failure message="Authorization: Bearer secret-token expected 200">boom</failure>
        </testcase>
      </testsuite>
    </testsuites>
    """
    path = tmp_path / "junit.xml"
    path.write_text(xml, encoding="utf-8")
    parsed = parse_junit(path)
    assert parsed["total"] == 3
    assert parsed["passed"] == 1
    assert parsed["failed"] == 1
    assert parsed["skipped"] == 1
    assert "secret-token" not in parsed["failures"][0]["message"]
    assert redact_message("password=hunter2") == "password=***"


def test_missing_junit_with_crash_is_not_a_pass(tmp_path: Path) -> None:
    summary = write_run_summary(
        tmp_path,
        environment="test",
        started_at="2026-11-10T18:00:00+08:00",
        finished_at="2026-11-10T18:00:02+08:00",
        wall_seconds=2,
        suite_rows=[{"name": "api", "exit_code": 1, "junit": str(tmp_path / "missing.xml")}],
        resources={"mem_available_mb": 1000},
    )
    assert summary["errors"] == 1
    assert summary["passed"] == 0
    text = (tmp_path / "summary.txt").read_text(encoding="utf-8")
    assert "总数: 0" in text
    assert "没有生成 junit" in text
    stored = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert stored["failures"][0]["suite"] == "api"


def test_run_cloud_dry_run_skips_browser_when_memory_is_low(tmp_path: Path) -> None:
    env = {
        **dict(**{key: value for key, value in __import__("os").environ.items()}),
        "QA_ROOT": str(tmp_path / "qa"),
        "QA_SKIP_BOOTSTRAP": "1",
        "QA_CLOUD_MEM_MB": "128",
    }
    result = subprocess.run(
        ["bash", "tools/run_cloud.sh", "--dry-run", "--suite", "ui", "-m", "smoke", "--workers", "1"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2, result.stderr
    assert "不启动浏览器" in result.stdout
    assert "run.py" not in result.stdout


def test_run_cloud_dry_run_named_test_is_a_single_command(tmp_path: Path) -> None:
    env = {
        **dict(**{key: value for key, value in __import__("os").environ.items()}),
        "QA_ROOT": str(tmp_path / "qa"),
        "QA_SKIP_BOOTSTRAP": "1",
        "QA_CLOUD_MEM_MB": "4096",
    }
    node = "tests/api/example_posts/test_posts.py::test_get_post_detail"
    result = subprocess.run(
        ["bash", "tools/run_cloud.sh", "--dry-run", "--reruns", "0", "--workers", "1", "--", node],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.count("[run_cloud]") == 1
    assert node in result.stdout
    assert "--suite ui" not in result.stdout


def test_run_cloud_dry_run_prints_api_command(tmp_path: Path) -> None:
    env = {
        **dict(**{key: value for key, value in __import__("os").environ.items()}),
        "QA_ROOT": str(tmp_path / "qa"),
        "QA_SKIP_BOOTSTRAP": "1",
        "QA_CLOUD_MEM_MB": "4096",
    }
    result = subprocess.run(
        ["bash", "tools/run_cloud.sh", "--dry-run", "--suite", "api", "-m", "smoke", "--workers", "1"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--cloud" in result.stdout
    assert "--reruns 0" in result.stdout
    assert "--suite api" in result.stdout
    assert "-m smoke" in result.stdout
    assert "-n " not in result.stdout
    assert "run_dir=" in result.stdout
