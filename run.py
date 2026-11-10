#!/usr/bin/env python3
"""统一执行入口：选环境和用例集，按 marker 过滤，失败默认重跑 2 次，并生成 Allure 结果和 HTML 报告。

示例（在仓库根目录执行）：
  python run.py --env test --suite api -m smoke
  python run.py --suite ui --reruns 0 -- --headed -x
  python run.py --cloud --suite api -m smoke
  python run.py --alluredir= --html= -- tests/api/example_posts/test_posts.py -vv

run.py 不认识的参数，以及 -- 之后的参数，原样追加到 pytest 命令末尾。
pytest 在仓库根目录运行，相对路径都相对仓库根目录。
退出码就是 pytest 的退出码：0 全部通过，1 有用例失败，5 没有收集到用例。
--cloud 在内存不足以打开浏览器时返回 2，不启动 pytest。
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shlex
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

from config.environment import ENVIRONMENTS, load_environment
from tools.cloud_efficiency import allow_browser, mem_available_mb, plan_suite, ui_pytest_args, worker_count

ROOT = Path(__file__).resolve().parent
# all 不传目录，交给 pytest.ini 的 testpaths：这样 -- 后面给出的文件或节点 ID 不会被整个 tests/ 盖过。
SUITE_PATHS = {"all": [], "api": ["tests/api"], "ui": ["tests/ui"]}


def non_negative_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"需要整数，收到 {value!r}") from None
    if number < 0:
        raise argparse.ArgumentTypeError("不能小于 0")
    return number


def build_parser() -> argparse.ArgumentParser:
    # allow_abbrev=False：只认完整的参数名，其余参数一律交给 pytest。
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, allow_abbrev=False
    )
    parser.add_argument(
        "--env",
        type=str.lower,
        choices=list(ENVIRONMENTS),
        help="目标环境，写入 ENVIRONMENT；不传时沿用环境变量或 .env 中的值，都没有时为 test",
    )
    parser.add_argument("--suite", choices=list(SUITE_PATHS), default="all", help="用例集，默认 %(default)s")
    parser.add_argument("-m", "--markers", metavar="EXPR", help='marker 表达式，例如 "smoke and not ui"')
    parser.add_argument(
        "--reruns",
        type=non_negative_int,
        default=None,
        metavar="N",
        help="失败重跑次数；默认 2，--cloud 时默认 0；0 表示不重跑",
    )
    parser.add_argument(
        "--workers",
        type=non_negative_int,
        default=None,
        metavar="N",
        help="并行进程数。大于 1 且已安装 pytest-xdist 时传给 -n；0 或 1 表示串行。--cloud 不传时按内存自动决定",
    )
    parser.add_argument(
        "--cloud",
        action="store_true",
        help="Bot 云电脑：失败不重跑，按内存限制并发，UI 只保留失败截图和 trace，HTML 不内嵌资源",
    )
    parser.add_argument(
        "--alluredir",
        default="reports/allure-results",
        metavar="DIR",
        help="Allure 结果目录，默认 %(default)s；写成 --alluredir= 表示不生成",
    )
    parser.add_argument(
        "--html",
        metavar="FILE",
        help="单文件 HTML 报告，默认 reports/html/<suite>-report.html；写成 --html= 表示不生成",
    )
    return parser


def format_command(command: list[str]) -> str:
    return subprocess.list2cmdline(command) if os.name == "nt" else shlex.join(command)


def xdist_available() -> bool:
    return importlib.util.find_spec("xdist") is not None


# 这些 pytest 参数后面跟的是值，不是用例节点。
_OPTIONS_WITH_VALUE = {
    "--output",
    "--browser",
    "--browser-channel",
    "--tracing",
    "--screenshot",
    "--video",
    "-n",
    "--numprocesses",
    "--reruns",
    "--reruns-delay",
    "-m",
    "-k",
    "-p",
    "--override-ini",
    "--tb",
    "--maxfail",
    "--timeout",
    "--dist",
}


def pytest_targets(pytest_args: list[str]) -> list[str]:
    """`--` 后面点名的文件或节点。有这些参数时不再附带整个 tests/api 或 tests/ui。"""
    targets: list[str] = []
    skip_next = False
    for arg in pytest_args:
        if skip_next:
            skip_next = False
            continue
        if arg in _OPTIONS_WITH_VALUE:
            skip_next = True
            continue
        if not arg or arg.startswith("-"):
            continue
        targets.append(arg)
    return targets


def looks_like_ui(targets: list[str]) -> bool:
    return any("/ui/" in target or target.startswith("tests/ui") for target in targets)


def build_pytest_command(
    *,
    python: str,
    suite: str,
    markers: str | None,
    reruns: int,
    alluredir: str,
    html: str,
    pytest_args: list[str],
    workers: int,
    ui_artifacts: bool,
    self_contained_html: bool,
) -> list[str]:
    paths = [] if pytest_targets(pytest_args) else list(SUITE_PATHS[suite])
    command = [python, "-m", "pytest", *paths]
    if markers:
        command += ["-m", markers]
    if reruns:
        command += ["--reruns", str(reruns)]
    if workers > 1:
        command += ["-n", str(workers)]
    if alluredir:
        command.append(f"--alluredir={alluredir}")
    if html:
        command.append(f"--html={html}")
        if self_contained_html:
            command.append("--self-contained-html")
    if ui_artifacts:
        command += ui_pytest_args(pytest_args, "reports/playwright")
    else:
        command += pytest_args
    return command


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args, pytest_args = parser.parse_known_args(argv)
    if "--" in pytest_args:
        pytest_args.remove("--")  # argparse 会把分隔符 -- 也留在剩余参数里

    # 优先级与 config/settings.py 一致：--env > 环境变量 > .env > 默认值。
    load_dotenv(ROOT / ".env")
    if args.env:
        os.environ["ENVIRONMENT"] = args.env
    try:
        environment = load_environment().name
    except ValueError as exc:
        parser.error(str(exc))
    os.environ["ENVIRONMENT"] = environment

    reruns = 0 if args.cloud else 2
    if args.reruns is not None:
        reruns = args.reruns
    markers = args.markers
    suite = args.suite
    workers = 0 if args.workers is None else args.workers
    ui_artifacts = False
    targets = pytest_targets(pytest_args)
    if args.cloud:
        mem_mb = mem_available_mb()
        cpu = os.cpu_count() or 1
        force_ui = os.environ.get("QA_CLOUD_FORCE_UI") == "1"
        # 点名了节点时不再套 plan_suite 的「all → 只跑接口」降级，避免把整个 tests/api 加回来。
        if targets:
            target_ui = looks_like_ui(targets) or args.suite == "ui"
            if target_ui and not allow_browser(mem_mb, force=force_ui):
                print(f"[run.py] 可用内存 {mem_mb}MB，低于 800MB，不启动浏览器", flush=True)
                return 2
            kind = "ui" if target_ui else "api"
            workers = worker_count(kind, mem_mb=mem_mb, cpu=cpu, explicit=args.workers)
            ui_artifacts = target_ui
            suite = "all"
        else:
            plan = plan_suite(
                suite=args.suite,
                markers=args.markers,
                mem_mb=mem_mb,
                cpu=cpu,
                explicit_workers=args.workers,
                force_ui=force_ui,
            )
            if plan.blocked:
                print(f"[run.py] {plan.blocked}", flush=True)
                return 2
            if plan.note:
                print(f"[run.py] {plan.note}", flush=True)
            suite = plan.suite
            markers = plan.markers
            workers = plan.workers
            ui_artifacts = plan.ui_artifacts
    if workers > 1 and not xdist_available():
        print("[run.py] 未安装 pytest-xdist，改为串行", flush=True)
        workers = 1

    if args.cloud and args.html is None:
        html = ""
    elif args.html is None:
        html = f"reports/html/{suite}-report.html"
    else:
        html = args.html

    command = build_pytest_command(
        python=sys.executable,
        suite=suite,
        markers=markers,
        reruns=reruns,
        alluredir=args.alluredir,
        html=html,
        pytest_args=pytest_args,
        workers=workers,
        ui_artifacts=ui_artifacts,
        self_contained_html=bool(html) and not args.cloud,
    )

    print(f"[run.py] ENVIRONMENT={environment}", flush=True)
    print(f"[run.py] {format_command(command)}", flush=True)
    process = subprocess.Popen(command, cwd=ROOT)
    try:
        return process.wait()
    except KeyboardInterrupt:
        # Ctrl+C 同时发给了 pytest，等它打印总结、写完报告再退出。
        return process.wait()


if __name__ == "__main__":
    sys.exit(main())
