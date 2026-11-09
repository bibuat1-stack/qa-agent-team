"""Lifecycle tests for tools/ask_cursor.py. No network."""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("ask_cursor", ROOT / "tools" / "ask_cursor.py")
ask = importlib.util.module_from_spec(SPEC)
sys.modules["ask_cursor"] = ask
assert SPEC.loader is not None
SPEC.loader.exec_module(ask)

PROBLEM = "帖子详情接口连续失败，断言读不到 title 字段，需要专家看日志。"
REPO = "https://github.com/bibuat1-stack/qa-agent-team"
AGENT = "bc-12345678-1234-4234-8234-123456789abc"
AGENT_URL = f"https://cursor.com/agents/{AGENT}"
WHY = "验证失败：失败用例和所在模块重跑后断言仍然错误，详见新日志。"
NODE_A = "tests/api/example_posts/test_posts.py::TestPosts::test_case_1"
NODE_B = "tests/api/example_posts/test_posts.py::TestPosts::test_case_2"
STATUS_FIELDS = (
    "hash",
    "status",
    "mode",
    "round",
    "followups",
    "owner",
    "problem",
    "agent_url",
    "pr_url",
    "summary",
    "updated_at",
    "case_path",
    "next",
)


def run(capsys, argv: list[str]) -> tuple[int, dict]:
    code = ask.main(argv)
    payload = json.loads(capsys.readouterr().out)
    return code, payload


def write_log(directory: Path, name: str, text: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


def failure_log(node: str, detail: str = "1", token: str = "abc123def4567890") -> str:
    return f"FAILED {node} - AssertionError: expected {detail} got 2 id={token}\n"


def load_ledger(root: Path) -> dict:
    return json.loads((root / "ledger.json").read_text(encoding="utf-8"))


def budget_used(root: Path) -> int:
    return sum(int(value) for value in load_ledger(root)["days"].values())


def prepare(
    capsys,
    root: Path,
    evidence: Path,
    *,
    mode: str = "fix",
    repo: str = REPO,
    problem: str = PROBLEM,
    budget: str = "3",
    owner: str = "",
    extra: list[str] | None = None,
) -> tuple[int, dict]:
    argv = [
        "prepare",
        "--root",
        str(root),
        "--mode",
        mode,
        "--problem",
        problem,
        "--evidence",
        str(evidence),
        "--budget",
        budget,
    ]
    if repo:
        argv.extend(["--repo", repo])
    if owner:
        argv.extend(["--owner", owner])
    if extra:
        argv.extend(extra)
    return run(capsys, argv)


def test_prepare_refuses_short_problem_missing_evidence_and_fix_without_repo(tmp_path, capsys):
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))

    code, data = run(
        capsys,
        ["prepare", "--root", str(root), "--mode", "advise", "--problem", "太短", "--evidence", str(log)],
    )
    assert code == 2
    assert data["decision"] == "refused"

    code, data = run(
        capsys,
        ["prepare", "--root", str(root), "--mode", "advise", "--problem", PROBLEM],
    )
    assert code == 2
    assert data["decision"] == "refused"
    assert "证据" in data["reason"]

    code, data = run(
        capsys,
        ["prepare", "--root", str(root), "--mode", "fix", "--problem", PROBLEM, "--evidence", str(log)],
    )
    assert code == 2
    assert data["decision"] == "refused"
    assert "repo" in data["reason"]
    assert not (root / "ledger.json").exists()


def test_prepare_writes_case_and_pending_duplicate_does_not_charge_twice(tmp_path, capsys):
    assert ask.clip_owner("测" * 50) == "测" * 40
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    code, data = prepare(
        capsys,
        root,
        log,
        owner="失败分诊员",
        extra=["--context", "上次修复没有覆盖这个字段。", "--ref", "main"],
    )
    assert code == 0
    assert data["decision"] == "allowed"
    assert data["budget_left"] == 2
    key = data["hash"]
    folder = root / key
    brief = (folder / "brief.md").read_text(encoding="utf-8")
    assert "第 1 轮" in brief
    assert PROBLEM in brief
    assert (folder / "problem.md").read_text(encoding="utf-8").strip() == PROBLEM
    assert (folder / "context.md").exists()
    assert (folder / "case.md").exists()
    assert "+08:00" in (folder / "case.md").read_text(encoding="utf-8")
    request = json.loads((folder / "request.json").read_text(encoding="utf-8"))
    assert request["kind"] == "create"
    item = load_ledger(root)["items"][key]
    assert item["status"] == "pending"
    assert item["round"] == 1
    assert item["followups"] == 0
    assert item["owner"] == "失败分诊员"
    assert item["repo"] == REPO
    assert item["ref"] == "main"
    assert item["agent_id"] == item["requested_agent_id"]
    assert item["agent_id"].startswith("bc-")
    assert budget_used(root) == 1

    code, again = prepare(capsys, root, log, owner="失败分诊员", extra=["--context", "上次修复没有覆盖这个字段。", "--ref", "main"])
    assert code == 3
    assert again["decision"] == "duplicate"
    assert again["hash"] == key
    assert again["status"] == "pending"
    assert again["case_path"] == str(folder)
    assert "brief.md" in again["next"]
    assert "等待" not in again["next"]
    assert (folder / "brief.md").read_text(encoding="utf-8") == brief
    assert budget_used(root) == 1

    ledger = load_ledger(root)
    aged = (ask.dt.datetime.now(ask.TZ) - ask.dt.timedelta(hours=48)).isoformat(timespec="microseconds")
    ledger["items"][key]["created_at"] = aged
    (root / "ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
    code, aged_result = prepare(capsys, root, log)
    assert code == 3
    assert aged_result["decision"] == "duplicate"
    assert aged_result["hash"] == key
    assert budget_used(root) == 1
    assert (folder / "brief.md").read_text(encoding="utf-8") == brief

    code, recorded = run(
        capsys,
        ["record", "--root", str(root), "--hash", key, "--status", "pending", "--agent-url", AGENT_URL],
    )
    assert code == 0
    assert recorded["agent_id"] == AGENT
    code, waiting = prepare(capsys, root, log)
    assert code == 3
    assert waiting["decision"] == "duplicate"
    assert "等待" in waiting["next"]
    assert budget_used(root) == 1
    assert not (root / ".ledger.lock").exists()


def test_node_ids_keep_same_case_and_split_different_cases(tmp_path, capsys):
    same_a = ask.failure_signature(PROBLEM, [failure_log(NODE_A, "1", "abc123def4567890")])
    same_b = ask.failure_signature(PROBLEM, [failure_log(NODE_A, "9", "fff000aaa111bbb2")])
    other = ask.failure_signature(PROBLEM, [failure_log(NODE_B, "1", "abc123def4567890")])
    assert same_a == same_b
    assert same_a != other
    assert same_a.startswith(NODE_A + " ")

    junit_a = "tests.api.example_posts.test_posts.TestPosts::test_get_post_detail"
    junit_b = "tests.api.example_posts.test_posts.TestPosts::test_list_posts"
    assert ask.failure_signature(
        "x", [f"FAILED {junit_a} AssertionError: boom 11 id=0123456789abcdef\n"]
    ) == ask.failure_signature("x", [f"FAILED {junit_a} AssertionError: boom 99 id=fedcba9876543210\n"])
    assert ask.failure_signature("x", [f"FAILED {junit_a} AssertionError: boom 11\n"]) != ask.failure_signature(
        "x", [f"FAILED {junit_b} AssertionError: boom 11\n"]
    )
    ambiguous = "需求编号 123 对空列表的理解不确定，请判断边界"
    assert ask.failure_signature(ambiguous, []) == ask.failure_signature(ambiguous.replace("123", "999"), [])
    assert ask.failure_signature("需求对空列表算通过还是失败没有写清楚啊", []) != ask.failure_signature(
        "需求对超长标题是截断还是拒绝没有写清楚啊", []
    )

    root = tmp_path / "esc"
    first = write_log(tmp_path, "a1.log", failure_log(NODE_A, "1", "abc123def4567890"))
    second = write_log(tmp_path, "a2.log", failure_log(NODE_A, "9", "fff000aaa111bbb2"))
    third = write_log(tmp_path, "b.log", failure_log(NODE_B, "1", "abc123def4567890"))
    code, left = prepare(capsys, root, first)
    code_same, again = prepare(capsys, root, second)
    code_other, right = prepare(capsys, root, third)
    assert code == 0 and left["decision"] == "allowed"
    assert code_same == 3 and again["decision"] == "duplicate"
    assert again["hash"] == left["hash"]
    assert code_other == 0 and right["decision"] == "allowed"
    assert right["hash"] != left["hash"]


def test_record_answered_then_prepare_continues_without_charging(tmp_path, capsys):
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    code, created = prepare(capsys, root, log)
    assert code == 0
    key = created["hash"]
    code, _recorded = run(
        capsys,
        [
            "record",
            "--root",
            str(root),
            "--hash",
            key,
            "--status",
            "answered",
            "--summary",
            "已经有结论：字段路径写错",
            "--confidence",
            "0.7",
            "--agent-url",
            AGENT_URL,
        ],
    )
    assert code == 0
    ledger = load_ledger(root)
    ledger["items"][key]["created_at"] = (
        ask.dt.datetime.now(ask.TZ) - ask.dt.timedelta(hours=48)
    ).isoformat(timespec="microseconds")
    (root / "ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")

    code, data = prepare(capsys, root, log)
    assert code == 0
    assert data["decision"] == "continue"
    assert data["hash"] == key
    assert data["summary"] == "已经有结论：字段路径写错"
    assert budget_used(root) == 1
    assert load_ledger(root)["items"][key]["status"] == "answered"


def test_followup_keeps_hash_and_does_not_charge_budget(tmp_path, capsys):
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    _code, created = prepare(capsys, root, log)
    key = created["hash"]
    summary = "断言把 title 读成了 name"
    run(
        capsys,
        [
            "record",
            "--root",
            str(root),
            "--hash",
            key,
            "--status",
            "answered",
            "--summary",
            summary,
            "--confidence",
            "0.42",
            "--agent-url",
            AGENT_URL,
            "--pr-url",
            "https://github.com/bibuat1-stack/qa-agent-team/pull/4",
        ],
    )
    fresh = write_log(tmp_path, "fresh.log", failure_log(NODE_A, "3"))
    code, data = run(
        capsys,
        ["followup", "--root", str(root), "--hash", key, "--why", WHY, "--evidence", str(fresh), "--budget", "3"],
    )
    assert code == 0
    assert data["decision"] == "followup"
    assert data["hash"] == key
    assert data["round"] == 2
    assert data["followups"] == 1
    text = (root / key / "followup.md").read_text(encoding="utf-8")
    assert summary in text
    assert "最终回复的最后必须是且只能有一个 json 代码块" in text
    assert "不可信" in text
    assert (root / key / "followup-2.md").read_text(encoding="utf-8") == text
    assert budget_used(root) == 1
    item = load_ledger(root)["items"][key]
    assert item["round"] == 2
    assert item["status"] == "pending"


def test_followup_while_pending_does_not_increment_round(tmp_path, capsys):
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    _code, created = prepare(capsys, root, log)
    key = created["hash"]
    marker = "这条追问不应该被写进任何案例文件里面"
    code, data = run(
        capsys,
        ["followup", "--root", str(root), "--hash", key, "--why", marker, "--evidence", str(log)],
    )
    assert code == 3
    assert data["decision"] == "already_pending"
    assert data["round"] == 1
    assert data["prompt_path"].endswith("brief.md")
    folder = root / key
    assert not (folder / "followup.md").exists()
    assert marker not in (folder / "brief.md").read_text(encoding="utf-8")
    item = load_ledger(root)["items"][key]
    assert item["round"] == 1
    assert item["followups"] == 0
    assert budget_used(root) == 1

    code, missing = run(
        capsys,
        ["followup", "--root", str(root), "--hash", "0123456789abcdef", "--why", WHY, "--evidence", str(log)],
    )
    assert code == 2
    assert "未知 hash" in missing["error"]


def test_followup_cap_blocks_and_reopen_keeps_the_hash(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("ASK_CURSOR_FOLLOWUPS", "1")
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    _code, created = prepare(capsys, root, log, budget="3")
    key = created["hash"]
    run(capsys, ["record", "--root", str(root), "--hash", key, "--status", "answered", "--summary", "先记下第一轮结论"])
    code, first = run(
        capsys,
        ["followup", "--root", str(root), "--hash", key, "--why", WHY, "--evidence", str(log), "--budget", "3"],
    )
    assert code == 0
    assert first["round"] == 2
    assert budget_used(root) == 1
    run(capsys, ["record", "--root", str(root), "--hash", key, "--status", "answered", "--summary", "验证仍失败"])
    before = (root / key / "followup.md").read_text(encoding="utf-8")
    blocked_why = "这次追问超过上限，不应当覆盖已经写好的 followup 文件"
    code, blocked = run(
        capsys,
        ["followup", "--root", str(root), "--hash", key, "--why", blocked_why, "--evidence", str(log), "--budget", "3"],
    )
    assert code == 3
    assert blocked["decision"] == "followups_exhausted"
    assert blocked["status"] == "blocked"
    assert blocked["hash"] == key
    assert load_ledger(root)["items"][key]["round"] == 2
    assert (root / key / "followup.md").read_text(encoding="utf-8") == before
    assert budget_used(root) == 1

    code, denied = run(
        capsys,
        [
            "followup",
            "--root",
            str(root),
            "--hash",
            key,
            "--reopen",
            "--why",
            WHY,
            "--evidence",
            str(log),
            "--budget",
            "1",
        ],
    )
    assert code == 4
    assert denied["decision"] == "budget_exhausted"
    assert load_ledger(root)["items"][key]["status"] == "blocked"
    assert budget_used(root) == 1

    reopen_why = "人工要求重开这个案例，继续看同一条失败日志。"
    code, reopened = run(
        capsys,
        [
            "followup",
            "--root",
            str(root),
            "--hash",
            key,
            "--reopen",
            "--why",
            reopen_why,
            "--evidence",
            str(log),
            "--budget",
            "3",
        ],
    )
    assert code == 0
    assert reopened["hash"] == key
    assert reopened["decision"] == "followup"
    assert reopened["round"] == 3
    assert reopened["followups"] == 1
    assert reopen_why in (root / key / "followup.md").read_text(encoding="utf-8")
    assert budget_used(root) == 2
    assert load_ledger(root)["items"][key]["status"] == "pending"


def test_verified_is_hidden_unless_status_all(tmp_path, capsys):
    root = tmp_path / "esc"
    first = write_log(tmp_path, "a.log", failure_log(NODE_A))
    second = write_log(tmp_path, "b.log", failure_log(NODE_B))
    _code, left = prepare(capsys, root, first, budget="5")
    _code, right = prepare(capsys, root, second, budget="5")
    pr_url = "https://github.com/bibuat1-stack/qa-agent-team/pull/12"
    code, _recorded = run(
        capsys,
        [
            "record",
            "--root",
            str(root),
            "--hash",
            left["hash"],
            "--status",
            "verified",
            "--pr-url",
            pr_url,
            "--summary",
            "验证通过",
        ],
    )
    assert code == 0
    assert "不要合并" in load_ledger(root)["items"][left["hash"]]["next"]

    code, data = run(capsys, ["status", "--root", str(root)])
    assert code == 0
    assert [case["hash"] for case in data["cases"]] == [right["hash"]]
    for field in STATUS_FIELDS:
        assert field in data["cases"][0]

    code, data = run(capsys, ["status", "--root", str(root), "--all"])
    assert [case["hash"] for case in data["cases"]] == [left["hash"], right["hash"]]
    assert data["cases"][0]["status"] == "verified"

    code, one = run(capsys, ["status", "--root", str(root), "--hash", left["hash"]])
    assert code == 0
    assert one["status"] == "verified"
    assert one["brief_path"].endswith("brief.md")
    assert one["pr_url"] == pr_url

    code, filtered = run(capsys, ["status", "--root", str(root), "--pr-url", "pull/12"])
    assert filtered["cases"] == []
    code, filtered = run(capsys, ["status", "--root", str(root), "--all", "--pr-url", "pull/12"])
    assert [case["hash"] for case in filtered["cases"]] == [left["hash"]]

    code, missing = run(capsys, ["status", "--root", str(root), "--hash", "0123456789abcdef"])
    assert code == 2
    assert not (root / ".ledger.lock").exists()


def test_evidence_secrets_are_redacted_from_the_brief(tmp_path, capsys):
    root = tmp_path / "esc"
    log = write_log(
        tmp_path,
        "secret.log",
        "Authorization: Bearer supersecretTOKEN123\n"
        "password=supersecretvalue\n"
        + failure_log(NODE_A),
    )
    code, data = prepare(capsys, root, log)
    assert code == 0
    brief = Path(data["brief_path"]).read_text(encoding="utf-8")
    request = Path(data["request_path"]).read_text(encoding="utf-8")
    assert "supersecretTOKEN123" not in brief
    assert "supersecretvalue" not in brief
    assert "supersecretTOKEN123" not in request
    assert "supersecretvalue" not in request
    assert "AssertionError" in brief


def test_api_dry_run_create_then_followup_prompt_only(tmp_path, capsys):
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    _code, created = prepare(capsys, root, log)
    key = created["hash"]
    code, dry = run(capsys, ["api", "--root", str(root), "--hash", key])
    assert code == 0
    assert dry["dry_run"] is True
    assert dry["POST"] == "https://api.cursor.com/v1/agents"
    assert not dry["POST"].endswith("/runs")
    assert dry["body"]["kind"] == "create"

    run(
        capsys,
        [
            "record",
            "--root",
            str(root),
            "--hash",
            key,
            "--status",
            "answered",
            "--summary",
            "第一轮结论",
            "--agent-url",
            AGENT_URL,
        ],
    )
    code, _followed = run(
        capsys,
        ["followup", "--root", str(root), "--hash", key, "--why", WHY, "--evidence", str(log)],
    )
    assert code == 0
    code, dry = run(capsys, ["api", "--root", str(root), "--hash", key])
    assert code == 0
    assert dry["POST"] == f"https://api.cursor.com/v1/agents/{AGENT}/runs"
    assert set(dry["body"]) == {"prompt"}
    assert set(dry["body"]["prompt"]) == {"text"}
    assert "model" not in dry["body"]
    assert "repos" not in dry["body"]
    assert "autoCreatePR" not in dry["body"]

    legacy_root = tmp_path / "legacy-root"
    legacy_hash = "abcdef1234567890"
    legacy_dir = legacy_root / legacy_hash
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "request.json").write_text(
        json.dumps({"agentId": AGENT, "prompt": {"text": "旧文件没有 kind"}}),
        encoding="utf-8",
    )
    code, legacy = run(capsys, ["api", "--root", str(legacy_root), "--hash", legacy_hash])
    assert code == 0
    assert legacy["POST"] == "https://api.cursor.com/v1/agents"


def test_followup_409_does_not_replace_summary(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    _code, created = prepare(capsys, root, log)
    key = created["hash"]
    summary = "原先的诊断结论保持不变"
    run(
        capsys,
        [
            "record",
            "--root",
            str(root),
            "--hash",
            key,
            "--status",
            "answered",
            "--summary",
            summary,
            "--confidence",
            "0.55",
            "--agent-url",
            AGENT_URL,
        ],
    )
    run(capsys, ["followup", "--root", str(root), "--hash", key, "--why", WHY, "--evidence", str(log)])
    calls = []

    def fake(key_arg, method, path, body=None):
        calls.append((method, path, body))
        return 409, {
            "code": "agent_busy",
            "error": "agent_busy",
            "result": '```json\n{"diagnosis": "旧结论不应该写回", "solution": "不要采用", "confidence": 0.99}\n```',
            "latestRunId": "run-old",
            "status": "FINISHED",
            "run": {"id": "run-old", "status": "FINISHED", "result": "旧结论不应该写回"},
        }

    monkeypatch.setattr(ask, "call_api", fake)

    def fail_sleep(*_args, **_kwargs):
        raise AssertionError("unexpected sleep")

    monkeypatch.setattr(ask.time, "sleep", fail_sleep)
    code, data = run(capsys, ["api", "--root", str(root), "--hash", key, "--send"])
    assert code == 6
    assert data["status"] == "pending"
    assert calls == [("POST", f"/v1/agents/{AGENT}/runs", calls[0][2])]
    assert set(calls[0][2]) == {"prompt"}
    item = load_ledger(root)["items"][key]
    assert item["summary"] == summary
    assert item["confidence"] == 0.55
    blob = (root / "ledger.json").read_text(encoding="utf-8")
    assert "旧结论不应该写回" not in blob
    assert "旧结论不应该写回" not in (root / key / "case.md").read_text(encoding="utf-8")
    assert "旧结论不应该写回" not in (root / key / "timeline.json").read_text(encoding="utf-8")


def test_parse_answer_uses_last_json_block_or_fallback():
    text = """
先看到一版
```json
{"diagnosis": "first", "solution": "a", "confidence": 0.2}
```
最后一版才算数
```json
{"diagnosis": "字段路径错了", "solution": "改断言", "confidence": 0.9}
```
"""
    parsed = ask.parse_answer(text)
    assert parsed == {"diagnosis": "字段路径错了", "solution": "改断言", "confidence": 0.9}
    fallback = ask.parse_answer("只有一段话，没有 json 代码块")
    assert fallback["confidence"] == 0.3
    assert fallback["solution"] == ""
    assert "只有一段话" in fallback["diagnosis"]
    assert ask.parse_answer("```json\n{bad}\n```")["confidence"] == 0.3


def test_api_finished_run_parses_answer_and_fallback(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")

    def fail_sleep(*_args, **_kwargs):
        raise AssertionError("unexpected sleep")

    monkeypatch.setattr(ask.time, "sleep", fail_sleep)

    def drive(root: Path, result: str) -> dict:
        log = write_log(root, "log.txt", failure_log(NODE_A))
        _code, created = prepare(capsys, root, log)
        key = created["hash"]

        def fake(_key, method, path, body=None):
            if method == "POST":
                return 200, {"agent": {"id": AGENT, "url": AGENT_URL}, "run": {"id": "run-1"}}
            return 200, {
                "id": "run-1",
                "status": "FINISHED",
                "result": result,
                "git": {
                    "branches": [
                        {
                            "repoUrl": REPO,
                            "branch": "cursor/fix",
                            "prUrl": "https://github.com/bibuat1-stack/qa-agent-team/pull/15",
                        }
                    ]
                },
            }

        monkeypatch.setattr(ask, "call_api", fake)
        code, data = run(capsys, ["api", "--root", str(root), "--hash", key, "--send"])
        assert code == 0
        item = load_ledger(root)["items"][key]
        case = (root / key / "case.md").read_text(encoding="utf-8")
        return {"payload": data, "item": item, "case": case}

    parsed = drive(
        tmp_path / "ok",
        '前文\n```json\n{"diagnosis": "first", "solution": "no", "confidence": 0.1}\n```\n'
        '```json\n{"diagnosis": "字段路径错了", "solution": "改断言", "confidence": 0.82}\n```\n',
    )
    assert parsed["item"]["confidence"] == 0.82
    assert parsed["item"]["summary"] == "字段路径错了"
    assert parsed["item"]["solution"] == "改断言"
    assert parsed["payload"]["pr_url"].endswith("/pull/15")
    assert "字段路径错了" in parsed["case"]

    fallback = drive(tmp_path / "plain", "没有 json 代码块，只有一段说明。")
    assert fallback["item"]["confidence"] == 0.3
    assert "没有 json 代码块" in fallback["item"]["summary"]


def test_call_api_tolerates_non_json_error_body(monkeypatch):
    def boom(request, timeout=30):
        raise urllib.error.HTTPError(request.full_url, 502, "bad gateway", None, io.BytesIO(b"<html>nope</html>"))

    monkeypatch.setattr(ask.urllib.request, "urlopen", boom)
    status, body = ask.call_api("test-key", "POST", "/v1/agents", {"prompt": {"text": "x"}})
    assert status == 502
    assert "nope" in body["raw"]
    assert ask.decode_body(b"") == {}
    assert ask.decode_body(b"[1, 2]") == {"raw": [1, 2]}


def test_create_409_reuses_latest_run(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("CURSOR_API_KEY", "test-key")
    monkeypatch.setattr(ask.time, "sleep", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("sleep")))
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    _code, created = prepare(capsys, root, log)
    key = created["hash"]
    agent_id = json.loads((root / key / "request.json").read_text(encoding="utf-8"))["agentId"]
    calls = []

    def fake(_key, method, path, body=None):
        calls.append((method, path))
        if method == "POST":
            return 409, {"code": "already_exists"}
        if "/runs/" not in path:
            return 200, {"latestRunId": "run-9", "url": AGENT_URL}
        return 200, {
            "status": "FINISHED",
            "result": '```json\n{"diagnosis": "复用已有 run", "solution": "不用新开", "confidence": 0.7}\n```',
        }

    monkeypatch.setattr(ask, "call_api", fake)
    code, data = run(capsys, ["api", "--root", str(root), "--hash", key, "--send"])
    assert code == 0
    assert data["confidence"] == 0.7
    assert calls[0] == ("POST", "/v1/agents")
    assert calls[1] == ("GET", f"/v1/agents/{agent_id}")
    assert calls[2] == ("GET", f"/v1/agents/{agent_id}/runs/run-9")


def test_refund_keeps_pending_case_and_returns_budget(tmp_path, capsys):
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    _code, created = prepare(capsys, root, log)
    key = created["hash"]
    brief = (root / key / "brief.md").read_text(encoding="utf-8")
    code, data = run(
        capsys,
        ["record", "--root", str(root), "--hash", key, "--status", "answered", "--summary", "没启动", "--refund"],
    )
    assert code == 0
    assert data["refunded"] is True
    assert data["status"] == "pending"
    assert budget_used(root) == 0
    assert (root / key / "brief.md").read_text(encoding="utf-8") == brief
    code, again = prepare(capsys, root, log)
    assert code == 3
    assert again["decision"] == "duplicate"
    assert again["hash"] == key
    assert budget_used(root) == 0


def test_owner_accepts_a_non_qa_bot_name(tmp_path, capsys):
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    code, data = prepare(capsys, root, log, owner="运维巡检员")
    assert code == 0
    item = load_ledger(root)["items"][data["hash"]]
    assert item["owner"] == "运维巡检员"
    assert len(item["owner"]) <= 40
    assert "运维巡检员" in (root / data["hash"] / "case.md").read_text(encoding="utf-8")


def test_followup_refuses_fix_mode_without_repo(tmp_path, capsys):
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", "需求讨论记录里没有 pytest 节点，只是一句说明。\n")
    code, created = prepare(capsys, root, log, mode="advise", repo="")
    assert code == 0
    key = created["hash"]
    run(capsys, ["record", "--root", str(root), "--hash", key, "--status", "answered", "--summary", "仍然有两种读法"])
    code, data = run(
        capsys,
        ["followup", "--root", str(root), "--hash", key, "--mode", "fix", "--why", WHY, "--evidence", str(log)],
    )
    assert code == 2
    assert data["decision"] == "refused"
    assert "prepare --mode fix" in data["reason"]
    assert not (root / key / "followup.md").exists()
    assert load_ledger(root)["items"][key]["mode"] == "advise"


def test_old_ledger_item_without_new_keys_stays_one_case(tmp_path, capsys):
    root = tmp_path / "esc"
    log = write_log(tmp_path, "log.txt", failure_log(NODE_A))
    signature = ask.failure_signature(PROBLEM, [log.read_text(encoding="utf-8")])
    key = ask.problem_hash("fix", REPO, signature)
    root.mkdir()
    (root / "ledger.json").write_text(
        json.dumps(
            {
                "days": {"2026-11-01": 1},
                "items": {
                    key: {
                        "created_at": "2026-11-01T10:00:00+08:00",
                        "mode": "fix",
                        "repo": REPO,
                        "status": "answered",
                        "agent_url": AGENT_URL,
                        "pr_url": "",
                        "confidence": 0.4,
                        "summary": "旧账本结论",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    code, data = prepare(capsys, root, log)
    assert code == 0
    assert data["decision"] == "continue"
    assert data["hash"] == key
    assert budget_used(root) == 1
    code, listed = run(capsys, ["status", "--root", str(root)])
    assert [case["hash"] for case in listed["cases"]] == [key]
    assert listed["cases"][0]["round"] == 1
    code, recorded = run(
        capsys,
        ["record", "--root", str(root), "--hash", key, "--status", "needs_followup"],
    )
    assert code == 0
    assert "followup" in recorded["next"]
    code, followed = run(
        capsys,
        ["followup", "--root", str(root), "--hash", key, "--why", WHY, "--evidence", str(log)],
    )
    assert code == 0
    assert followed["hash"] == key
    assert followed["api_ready"] is True
    assert AGENT in (root / key / "request.json").read_text(encoding="utf-8")
    assert "旧账本结论" in (root / key / "followup.md").read_text(encoding="utf-8")
