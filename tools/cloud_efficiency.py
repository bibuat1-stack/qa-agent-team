"""Bot 云电脑的并发规划和 JUnit 摘要。只使用标准库，便于在装依赖之前调用。"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

# 低于这个可用内存就不再新开 Chromium。接口用例仍可串行跑。
UI_MIN_MB = 800

_BEARER = re.compile(r"(?i)(bearer|basic)\s+\S+")
_ASSIGNED_SECRET = re.compile(
    r"(?i)(token|password|passwd|pwd|cookie|authorization)(['\"]?\s*[:=]\s*['\"]?)[^\s'\",]+"
)


@dataclass(frozen=True)
class SuitePlan:
    suite: str
    markers: str | None
    workers: int
    ui_artifacts: bool
    blocked: str | None = None
    note: str | None = None


def mem_available_mb(text: str | None = None) -> int | None:
    """读取 MemAvailable（MiB）。读不到时返回 None，调用方按保守默认处理。"""
    if text is None:
        try:
            text = Path("/proc/meminfo").read_text(encoding="utf-8")
        except OSError:
            return None
    for line in text.splitlines():
        if line.startswith("MemAvailable:"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                return int(parts[1]) // 1024
    return None


def allow_browser(mem_mb: int | None, *, force: bool = False) -> bool:
    if force:
        return True
    if mem_mb is None:
        return True
    return mem_mb >= UI_MIN_MB


def worker_count(suite: str, *, mem_mb: int | None, cpu: int, explicit: int | None = None) -> int:
    """并行进程数。0 表示串行（调用方不要加 pytest-xdist 的 -n）。

    显式传入的值优先，包括 0。自动模式下接口最多 4 个进程，UI 最多 2 个，
    并且按可用内存下调，避免同时开多个 Chromium 把云电脑打满。
    """
    if suite not in {"api", "ui"}:
        raise ValueError(f"worker_count 只接受 api 或 ui，收到 {suite}")
    if explicit is not None:
        if explicit < 0:
            raise ValueError("workers 不能小于 0")
        return explicit
    cpu = max(1, cpu)
    if suite == "ui":
        if not allow_browser(mem_mb):
            return 0
        if mem_mb is None or mem_mb < 2500:
            return 1
        return min(2, cpu)
    if mem_mb is None:
        return min(2, cpu)
    if mem_mb < 800:
        return 1
    if mem_mb < 2000:
        return min(2, cpu)
    return min(4, cpu)


def plan_suite(
    *,
    suite: str,
    markers: str | None,
    mem_mb: int | None,
    cpu: int,
    explicit_workers: int | None,
    force_ui: bool,
) -> SuitePlan:
    """为一轮 pytest 做资源计划。suite=all 且内存够时仍是一轮进程，并发按 UI 上限。"""
    if suite not in {"api", "ui", "all"}:
        raise ValueError(f"未知 suite：{suite}")
    if suite == "ui" and not allow_browser(mem_mb, force=force_ui):
        return SuitePlan(
            suite="ui",
            markers=markers,
            workers=0,
            ui_artifacts=False,
            blocked=f"可用内存 {mem_mb}MB，低于 {UI_MIN_MB}MB，不启动浏览器",
        )
    if suite == "all" and not allow_browser(mem_mb, force=force_ui):
        return SuitePlan(
            suite="api",
            markers=markers,
            workers=worker_count("api", mem_mb=mem_mb, cpu=cpu, explicit=explicit_workers),
            ui_artifacts=False,
            note=f"可用内存 {mem_mb}MB，本次只跑接口，跳过 UI",
        )
    if suite == "all":
        return SuitePlan(
            suite="all",
            markers=markers,
            workers=worker_count("ui", mem_mb=mem_mb, cpu=cpu, explicit=explicit_workers),
            ui_artifacts=True,
        )
    return SuitePlan(
        suite=suite,
        markers=markers,
        workers=worker_count(suite, mem_mb=mem_mb, cpu=cpu, explicit=explicit_workers),
        ui_artifacts=suite == "ui",
    )


def ui_pytest_args(pytest_args: list[str], output_dir: str | None = None) -> list[str]:
    """失败才留截图和 trace，关掉视频。调用方已经传过的选项保持不动。"""
    args = list(pytest_args)

    def has(option: str) -> bool:
        return any(item == option or item.startswith(option + "=") for item in args)

    prefix: list[str] = []
    if not has("--browser"):
        prefix += ["--browser", "chromium"]
    if not has("--tracing"):
        args += ["--tracing", "retain-on-failure"]
    if not has("--screenshot"):
        args += ["--screenshot", "only-on-failure"]
    if not has("--video"):
        args += ["--video", "off"]
    if output_dir and not has("--output"):
        args += ["--output", output_dir]
    return prefix + args


def redact_message(text: str) -> str:
    text = _BEARER.sub(r"\1 ***", text)
    text = _ASSIGNED_SECRET.sub(r"\1\2***", text)
    return text[:300]


def parse_junit(path: Path) -> dict:
    empty = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "duration_seconds": 0.0,
        "failures": [],
    }
    if not path.is_file():
        return {**empty, "missing": True}
    root = ET.parse(path).getroot()
    nodes = list(root.findall("testsuite")) if root.tag == "testsuites" else [root]
    total = failed = errors = skipped = 0
    duration = 0.0
    failures: list[dict[str, str]] = []
    for node in nodes:
        total += int(float(node.get("tests", "0") or 0))
        failed += int(float(node.get("failures", "0") or 0))
        errors += int(float(node.get("errors", "0") or 0))
        skipped += int(float(node.get("skipped", "0") or 0))
        duration += float(node.get("time", "0") or 0)
        for case in node.iter("testcase"):
            problem = case.find("failure")
            kind = "failure"
            if problem is None:
                problem = case.find("error")
                kind = "error"
            if problem is None:
                continue
            raw = (problem.get("message") or problem.text or "").strip()
            first = raw.splitlines()[0] if raw else ""
            classname = case.get("classname") or ""
            name = case.get("name") or ""
            test_id = f"{classname}::{name}" if classname else name
            failures.append({"test": test_id, "kind": kind, "message": redact_message(first)})
    return {
        "total": total,
        "passed": max(0, total - failed - errors - skipped),
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "duration_seconds": round(duration, 3),
        "failures": failures,
    }


def render_summary_text(summary: dict) -> str:
    lines = [
        f"总数: {summary['total']}",
        f"通过: {summary['passed']}",
        f"失败: {summary['failed']}",
        f"错误: {summary['errors']}",
        f"跳过: {summary['skipped']}",
        f"耗时: {summary['duration_seconds']}s",
        f"报告: {summary['run_dir']}/summary.json",
    ]
    if summary.get("note"):
        lines.append(f"说明: {summary['note']}")
    failures = summary.get("failures") or []
    if failures:
        lines.append("失败用例:")
        for item in failures:
            message = f" {item['message']}" if item.get("message") else ""
            lines.append(f"- {item['test']}{message}")
    blocked = [row["name"] for row in summary.get("suites", []) if row.get("blocked")]
    if blocked:
        lines.append("未跑: " + "、".join(blocked) + "（内存不足或被跳过，不能记为通过）")
    return "\n".join(lines) + "\n"


def write_run_summary(
    run_dir: Path,
    *,
    environment: str,
    started_at: str,
    finished_at: str,
    wall_seconds: float,
    suite_rows: list[dict],
    resources: dict,
) -> dict:
    """suite_rows 每项含 name、exit_code，以及 junit 路径或 blocked 原因。"""
    suites = []
    notes = []
    for row in suite_rows:
        if row.get("note"):
            notes.append(str(row["note"]))
        if row.get("blocked"):
            suites.append(
                {
                    "name": row["name"],
                    "exit_code": row.get("exit_code", 2),
                    "blocked": row["blocked"],
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 0,
                    "duration_seconds": 0.0,
                    "failures": [],
                }
            )
            continue
        parsed = parse_junit(Path(row["junit"]))
        exit_code = row.get("exit_code", 0)
        if parsed.get("missing") and exit_code not in (0, 5):
            parsed["errors"] = max(1, parsed["errors"])
            parsed["failures"] = [
                {
                    "test": row["name"],
                    "kind": "error",
                    "message": f"没有生成 junit，pytest 退出码 {exit_code}",
                }
            ]
        suites.append({"name": row["name"], "exit_code": exit_code, **parsed})

    failures = []
    for suite in suites:
        for item in suite.get("failures") or []:
            failures.append({"suite": suite["name"], **item})
    summary = {
        "run_dir": str(run_dir),
        "environment": environment,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": round(wall_seconds, 3),
        "total": sum(suite["total"] for suite in suites),
        "passed": sum(suite["passed"] for suite in suites),
        "failed": sum(suite["failed"] for suite in suites),
        "errors": sum(suite["errors"] for suite in suites),
        "skipped": sum(suite["skipped"] for suite in suites),
        "failures": failures,
        "suites": suites,
        "resources": resources,
        "note": "；".join(notes),
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (run_dir / "summary.txt").write_text(render_summary_text(summary), encoding="utf-8")
    return summary


def _parse_workers(value: str) -> int | None:
    if value == "":
        return None
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("workers 不能小于 0")
    return number


def _plan_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="cloud_efficiency plan")
    parser.add_argument("--suite", required=True, choices=["api", "ui", "all"])
    parser.add_argument("--markers", default="")
    parser.add_argument("--workers", type=_parse_workers, default=None)
    parser.add_argument("--mem-mb", type=int, default=-1)
    parser.add_argument("--cpu", type=int, default=0)
    parser.add_argument("--force-ui", action="store_true")
    args = parser.parse_args(argv)
    mem = None if args.mem_mb < 0 else args.mem_mb
    if mem is None and args.mem_mb < 0:
        mem = mem_available_mb()
    cpu = args.cpu or (os_cpu())
    plan = plan_suite(
        suite=args.suite,
        markers=args.markers or None,
        mem_mb=mem,
        cpu=cpu,
        explicit_workers=args.workers,
        force_ui=args.force_ui,
    )
    payload = {
        "suite": plan.suite,
        "markers": plan.markers or "",
        "workers": plan.workers,
        "ui_artifacts": plan.ui_artifacts,
        "blocked": plan.blocked or "",
        "note": plan.note or "",
        "mem_mb": mem if mem is not None else -1,
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 2 if plan.blocked else 0


def os_cpu() -> int:
    import os

    return os.cpu_count() or 1


def _summarize_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="cloud_efficiency summarize")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--environment", default="")
    parser.add_argument("--started-at", required=True)
    parser.add_argument("--finished-at", required=True)
    parser.add_argument("--wall-seconds", type=float, required=True)
    parser.add_argument("--resources-json", default="{}")
    parser.add_argument("--suites-json", required=True, help="suite 结果的 JSON 数组")
    args = parser.parse_args(argv)
    summary = write_run_summary(
        args.run_dir,
        environment=args.environment,
        started_at=args.started_at,
        finished_at=args.finished_at,
        wall_seconds=args.wall_seconds,
        suite_rows=json.loads(args.suites_json),
        resources=json.loads(args.resources_json),
    )
    print(args.run_dir / "summary.txt")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in {"plan", "summarize"}:
        print("usage: python -m tools.cloud_efficiency plan|summarize ...", file=sys.stderr)
        return 2
    command, rest = argv[0], argv[1:]
    if command == "plan":
        return _plan_main(rest)
    return _summarize_main(rest)


if __name__ == "__main__":
    sys.exit(main())
