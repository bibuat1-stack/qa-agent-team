"""三站生产前台安全路径入口。

用法见同目录 README.md。密码按本机、完整库、临时文件、环境变量这个顺序读取。
本脚本不把某一站以往的回收结果写成通过。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from credentials import EXIT_MISSING_SECRET, MissingSecret, load_password
from sites import ALLOWED_PHONES, SITES, get_site

EXIT_FAIL = 1
EXIT_UNVERIFIED = 3
EXIT_SKIP = 4
EXIT_UNCONFIRMED = 5
EXIT_FAIL_REVIEW = 6


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="T8T 三站生产前台安全路径")
    parser.add_argument("--site", required=True, choices=[*SITES, "all"])
    parser.add_argument(
        "--step",
        default="all",
        choices=["login", "nav", "wingo", "recall", "switch", "all"],
    )
    parser.add_argument("--phone", help="只能是 9959950001、9959950002、9959950003")
    parser.add_argument(
        "--evidence",
        help="证据目录。不要指向仓库。默认写到 /tmp/t8t-main-flow/",
    )
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args(argv)
    keys = list(SITES) if args.site == "all" else [args.site]
    results = []
    for key in keys:
        site = get_site(key)
        phone = args.phone or site["default_phone"]
        if phone not in ALLOWED_PHONES:
            print("测号只能是 9959950001、9959950002、9959950003。", file=sys.stderr)
            return EXIT_FAIL
        if key == "muskan" and args.phone is None:
            phone = "9959950001"
        try:
            password = load_password(phone)
        except MissingSecret as exc:
            print(str(exc), file=sys.stderr)
            return EXIT_MISSING_SECRET
        try:
            from browser_steps import run_flow
        except ModuleNotFoundError:
            print("缺少 playwright。先按仓库 requirements.txt 安装依赖。", file=sys.stderr)
            return EXIT_FAIL
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        evidence = Path(args.evidence) if args.evidence else Path("/tmp/t8t-main-flow") / f"{key}-{args.step}-{stamp}"
        if _inside_repo(evidence):
            print("证据目录不要放在仓库里。", file=sys.stderr)
            return EXIT_FAIL
        try:
            result = run_flow(site, phone, password, args.step, evidence, args.headed)
        except Exception as exc:
            text = str(exc).replace(password, "[redacted]")
            print(f"{site['name']} 运行中断：{text.splitlines()[0][:240]}", file=sys.stderr)
            return EXIT_UNVERIFIED
        result["evidence"] = str(evidence)
        results.append(result)
        _print_result(result)
    code = _exit_code(results)
    print(json.dumps({"exit": code, "evidence": [item["evidence"] for item in results]}, ensure_ascii=False))
    return code


def _print_result(result: dict) -> None:
    print(f"{result['name']} {result['entry']}")
    for check in result["checks"]:
        print(f"  {check['id']}: {check['verdict']} ({check['source']})")
    print(f"  证据: {result['evidence']}")


def _exit_code(results: list[dict]) -> int:
    verdicts = [check.get("verdict") for result in results for check in result.get("checks", [])]
    if "失败" in verdicts:
        return EXIT_FAIL
    if "失败待核" in verdicts:
        return EXIT_FAIL_REVIEW
    if any(item in ("阻塞", "未验证") for item in verdicts):
        return EXIT_UNVERIFIED
    if "待确认" in verdicts:
        return EXIT_UNCONFIRMED
    if "跳过" in verdicts:
        return EXIT_SKIP
    if verdicts and all(item in ("通过", "未测") for item in verdicts):
        return 0
    return EXIT_UNCONFIRMED


def _inside_repo(path: Path) -> bool:
    repo = Path(__file__).resolve().parents[3]
    try:
        path.resolve().relative_to(repo)
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
