"""run.py 的命令拼装。云电脑模式不改变本地默认的重跑次数。"""
from __future__ import annotations

from run import build_parser, build_pytest_command, pytest_targets


def test_parser_keeps_cloud_opt_in() -> None:
    parser = build_parser()
    args, extra = parser.parse_known_args(["--suite", "api", "--", "tests/api/example_posts/test_posts.py::test_x"])
    assert args.cloud is False
    assert args.reruns is None
    # argparse 会把分隔符留在剩余参数里，main() 再去掉。
    assert extra == ["--", "tests/api/example_posts/test_posts.py::test_x"]


def test_option_values_are_not_treated_as_tests() -> None:
    args = ["--output", "/tmp/playwright", "--junitxml=/tmp/junit.xml", "--browser", "chromium"]
    assert pytest_targets(args) == []
    command = build_pytest_command(
        python="python",
        suite="ui",
        markers="smoke",
        reruns=0,
        alluredir="reports/allure-results",
        html="",
        pytest_args=args,
        workers=1,
        ui_artifacts=True,
        self_contained_html=False,
    )
    assert "tests/ui" in command
    assert "/tmp/playwright" in command


def test_named_test_does_not_pull_in_the_whole_directory() -> None:
    command = build_pytest_command(
        python="python",
        suite="api",
        markers=None,
        reruns=0,
        alluredir="",
        html="",
        pytest_args=["tests/api/example_posts/test_posts.py::test_get_post_detail"],
        workers=1,
        ui_artifacts=False,
        self_contained_html=False,
    )
    assert "tests/api" not in command
    assert "tests/api/example_posts/test_posts.py::test_get_post_detail" in command


def test_local_default_still_reruns_and_embeds_html() -> None:
    command = build_pytest_command(
        python="python",
        suite="api",
        markers="smoke",
        reruns=2,
        alluredir="reports/allure-results",
        html="reports/html/api-report.html",
        pytest_args=["-vv"],
        workers=1,
        ui_artifacts=False,
        self_contained_html=True,
    )
    assert "--reruns" in command
    assert command[command.index("--reruns") + 1] == "2"
    assert "--self-contained-html" in command
    assert "-n" not in command
    assert command[-1] == "-vv"


def test_cloud_ui_command_is_lean() -> None:
    command = build_pytest_command(
        python="python",
        suite="ui",
        markers=None,
        reruns=0,
        alluredir="/workspace/qa/runs/demo/ui/allure-results",
        html="/workspace/qa/runs/demo/ui/report.html",
        pytest_args=["--junitxml=/workspace/qa/runs/demo/ui/junit.xml"],
        workers=2,
        ui_artifacts=True,
        self_contained_html=False,
    )
    assert "--reruns" not in command
    assert "--self-contained-html" not in command
    assert command[command.index("-n") + 1] == "2"
    assert "retain-on-failure" in command
    assert "only-on-failure" in command
    assert "--video" in command
    assert "tests/ui" in command
    assert "reports/playwright" in command
    assert "--junitxml=/workspace/qa/runs/demo/ui/junit.xml" in command
