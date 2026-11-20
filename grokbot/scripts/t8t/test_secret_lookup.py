"""取密顺序。只用临时文件和假数据，不访问生产，不读真实账号本。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import credentials
from credentials import MissingSecret, load_password
import run_main_flow

PHONE = "9959950001"
OTHER = "9959950002"


def _table(phone: str, password: str, project: str = "T8T") -> str:
    return (
        "| 环境 | 系统 | 域名 | 账号 | 密码 |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"| 生产 | {project} | example.test | {phone} | {password} |\n"
    )


def _isolate(monkeypatch, tmp_path: Path) -> None:
    for key in (
        "T8T_PASSWORD",
        "T8T_ACCOUNTS_MODULE",
        "T8T_SECRET_FILE",
        "T8T_QA_TEMP_MIRROR",
        "T8T_ACCOUNT_SHEET_POINTER",
        "T8T_GOOGLE_ACCESS_TOKEN",
        "GOOGLE_ACCESS_TOKEN",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr(credentials, "LOCAL_ACCOUNTS_PATH", tmp_path / "missing-local.md")
    monkeypatch.setattr(credentials, "POINTER_PATH", tmp_path / "missing-pointer.md")


def test_local_file_is_used_before_sheet_or_env(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    local = tmp_path / "qa-test-accounts.md"
    local.write_text(_table(PHONE, "pw-local"), encoding="utf-8")
    monkeypatch.setattr(credentials, "LOCAL_ACCOUNTS_PATH", local)
    monkeypatch.setenv("T8T_PASSWORD", "pw-env")

    def sheet_must_not_run(phone: str) -> str | None:
        raise AssertionError(phone)

    monkeypatch.setattr(credentials, "_from_sheet", sheet_must_not_run)
    assert load_password(PHONE) == "pw-local"


def test_missing_local_uses_sheet_mock(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    local = tmp_path / "qa-test-accounts.md"
    local.write_text(_table(OTHER, "pw-other"), encoding="utf-8")
    monkeypatch.setattr(credentials, "LOCAL_ACCOUNTS_PATH", local)
    seen = []

    def sheet(phone: str) -> str | None:
        seen.append(phone)
        return "pw-sheet"

    monkeypatch.setattr(credentials, "_from_sheet", sheet)
    assert load_password(PHONE) == "pw-sheet"
    assert seen == [PHONE]


def test_local_and_sheet_miss_then_temp_file(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setattr(credentials, "_from_sheet", lambda phone: None)
    temp = tmp_path / "handed-accounts.md"
    temp.write_text(_table(PHONE, "pw-temp"), encoding="utf-8")
    monkeypatch.setenv("T8T_SECRET_FILE", str(temp))
    assert load_password(PHONE) == "pw-temp"


def test_all_missing_exits_2(monkeypatch, tmp_path, capsys):
    _isolate(monkeypatch, tmp_path)
    monkeypatch.setattr(credentials, "_from_sheet", lambda phone: None)
    code = run_main_flow.main(["--site", "yy567", "--step", "login"])
    captured = capsys.readouterr()
    assert code == 2
    assert "退出码 2" in captured.err
    assert "pw-" not in captured.err
    assert "spreadsheets" not in captured.err


def test_module_exception_is_not_shown(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    module = tmp_path / "accounts.py"
    module.write_text(
        "def get_password(phone):\n    raise RuntimeError('pw-leaked')\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("T8T_ACCOUNTS_MODULE", str(module))
    monkeypatch.setattr(credentials, "_from_sheet", lambda phone: None)
    try:
        load_password(PHONE)
    except MissingSecret as exc:
        assert "pw-leaked" not in str(exc)
    else:
        raise AssertionError("expected MissingSecret")
