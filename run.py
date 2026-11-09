#!/usr/bin/env python3
"""统一执行入口：选环境和用例集，按 marker 过滤，失败默认重跑 2 次，并生成 Allure 结果和 HTML 报告。

示例（在仓库根目录执行）：
  python run.py --env test --suite api -m smoke
  python run.py --suite ui --reruns 0 -- --headed -x
  python run.py --alluredir= --html= -- tests/api/example_posts/test_posts.py -vv

run.py 不认识的参数，以及 -- 之后的参数，原样追加到 pytest 命令末尾。
pytest 在仓库根目录运行，相对路径都相对仓库根目录。
退出码就是 pytest 的退出码：0 全部通过，1 有用例失败，5 没有收集到用例。
"""
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

from config.environment import ENVIRONMENTS, load_environment

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
        default=2,
        metavar="N",
        help="失败重跑次数，默认 %(default)s；0 表示不重跑",
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

    command = [sys.executable, "-m", "pytest", *SUITE_PATHS[args.suite]]
    if args.markers:
        command += ["-m", args.markers]
    if args.reruns:
        command += ["--reruns", str(args.reruns)]
    if args.alluredir:
        command.append(f"--alluredir={args.alluredir}")
    html = f"reports/html/{args.suite}-report.html" if args.html is None else args.html
    if html:
        command += [f"--html={html}", "--self-contained-html"]
    command += pytest_args

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
