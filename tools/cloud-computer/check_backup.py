#!/usr/bin/env python3
"""检查云电脑脚本备份的约定：内存只提示不拦截，报告不带出密钥。不进入 pytest。"""
from __future__ import annotations

import json
import os
import stat
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOX_HEALTH = ROOT / "bin" / "box_health.py"
HTML_REPORT = ROOT / "bin" / "html_report.py"
QA_READY = ROOT / "qa-ready.sh"
FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)


def tiny_png() -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"\x00" + b"\xff\x00\x00"
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def write_proc(proc: Path, available_kib: int, swap_free_kib: int) -> None:
    proc.mkdir(parents=True)
    (proc / "meminfo").write_text(
        "\n".join(
            [
                "MemTotal:       16777216 kB",
                f"MemAvailable:   {available_kib} kB",
                "SwapTotal:      16777216 kB",
                f"SwapFree:       {swap_free_kib} kB",
                "Shmem:          0 kB",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (proc / "uptime").write_text("100 0\n", encoding="utf-8")
    (proc / "loadavg").write_text("0.01 0.02 0.03 1/1 1\n", encoding="utf-8")
    (proc / "mounts").write_text("", encoding="utf-8")
    pid = proc / "4242"
    pid.mkdir()
    fields = ["S", "0", *["0"] * 18]
    (pid / "stat").write_text("4242 (python) " + " ".join(fields) + "\n", encoding="utf-8")
    (pid / "comm").write_text("python\n", encoding="utf-8")
    (pid / "smaps_rollup").write_text("Pss:                   2048 kB\n", encoding="utf-8")
    (pid / "cmdline").write_bytes(b"python\0/tmp/run.py\0--token\0SUPERSECRETTOKEN\0")
    (pid / "environ").write_bytes(b"DISPLAY=:14\0QA_OWNER=tester\0API_TOKEN=SHOULD_NOT_LEAK\0")
    os.symlink("/usr/bin/python3", pid / "exe")
    os.symlink("/workspace/demo", pid / "cwd")


def run_health(proc: Path, qa: Path, tmp: Path, extra_env: dict[str, str], args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "BOX_PROC": str(proc),
            "QA_ROOT": str(qa),
            "BOX_TMP": str(tmp),
            "PYTHONIOENCODING": "utf-8",
            "LANG": "C.UTF-8",
        }
    )
    env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(BOX_HEALTH), *args],
        cwd=proc.parent,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_box_health(tmp: Path) -> None:
    low_proc = tmp / "proc-low"
    qa = tmp / "qa"
    box_tmp = tmp / "box-tmp"
    write_proc(low_proc, available_kib=1024 * 1024, swap_free_kib=0)
    leases = qa / "leases"
    leases.mkdir(parents=True)
    stale = leases / "account__demo__old.json"
    fresh = leases / "account__demo__new.json"
    stale.write_text('{"type":"account"}\n', encoding="utf-8")
    fresh.write_text('{"type":"account"}\n', encoding="utf-8")
    old_time = time.time() - 3 * 3600
    os.utime(stale, (old_time, old_time))
    gone = box_tmp / "playwright_oldprofile-1"
    kept = box_tmp / "playwright_keepprofile-1"
    gone.mkdir(parents=True)
    kept.mkdir()
    (gone / "marker").write_text("x", encoding="utf-8")
    (kept / "marker").write_text("x", encoding="utf-8")
    os.utime(gone, (old_time, old_time))
    os.utime(kept, (old_time, old_time))
    (low_proc / "4242" / "cmdline").write_bytes(
        b"python\0/tmp/run.py\0--token\0SUPERSECRETTOKEN\0playwright_keepprofile-1\0"
    )

    low = run_health(low_proc, qa, box_tmp, {}, ["--clean"])
    check(low.returncode == 0, f"低内存退出码应是 0，实际 {low.returncode}\n{low.stderr}")
    check("SwapFree 0 MiB" in low.stdout, "低内存摘要没有 SwapFree")
    check("python run.py" in low.stdout, "没有按脚本名归类，进程可能没被读到")
    check("tester" in low.stdout, "没有读到 QA_OWNER")
    check("不拦截" in low.stdout, "低内存摘要没有写明不拦截")
    check("提示总控：可用内存低于 2048 MiB" in low.stdout, "低内存没有在末尾提示总控")
    check("SUPERSECRETTOKEN" not in low.stdout, "体检输出带了命令行参数")
    check("SHOULD_NOT_LEAK" not in low.stdout, "体检输出带了环境变量")
    record = json.loads((qa / "runs" / "box-health" / "health.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    check(record["swap_free_mib"] == 0, f"swap_free_mib 不对：{record.get('swap_free_mib')}")
    check(record["low_memory"] is True, "低内存没有记 low_memory")
    check(record["blocks_operation"] is False, "低内存仍标记为拦截")
    check(record["hint_avail_mib"] == 2048, "提示门槛不是 2048")
    blob = (qa / "runs" / "box-health" / "latest.md").read_text(encoding="utf-8")
    check("SUPERSECRETTOKEN" not in blob and "SHOULD_NOT_LEAK" not in blob, "latest.md 带了密钥")
    check(not stale.exists() and fresh.exists(), "清理应只删除过期租约")
    check(not gone.exists() and kept.exists(), "清理应只删除没有进程引用的临时配置")

    high_proc = tmp / "proc-high"
    write_proc(high_proc, available_kib=8192 * 1024, swap_free_kib=8192 * 1024)
    overridden = run_health(high_proc, qa / "high", box_tmp / "unused", {"BOX_HINT_AVAIL_MIB": "10000"}, [])
    check(overridden.returncode == 0, f"调高提示门槛后不应拦截，退出码 {overridden.returncode}")
    check("只提示" in overridden.stdout, "高于默认、低于覆盖值时仍应只提示")

    normal = run_health(high_proc, qa / "normal", box_tmp / "unused2", {"BOX_HINT_AVAIL_MIB": "nope"}, [])
    check(normal.returncode == 0, f"非法门槛不应导致失败，退出码 {normal.returncode}")
    check("未低于门槛" in normal.stdout, "充足内存应写未低于门槛")
    check("提示总控：可用内存低于" not in normal.stdout, "充足内存不应提示拦截")
    check("SwapFree 8192 MiB" in normal.stdout, "没有记下 SwapFree 8192 MiB")
    normal_record = json.loads((qa / "normal" / "runs" / "box-health" / "health.jsonl").read_text(encoding="utf-8"))
    check(normal_record["swap_free_mib"] == 8192, "json 里的 SwapFree 不是 8192")
    check(normal_record["hint_avail_mib"] == 2048, "非法门槛应退回 2048")
    check(normal_record["low_memory"] is False, "充足内存不应标低")


def test_live_proc(tmp: Path) -> None:
    qa = tmp / "live-qa"
    env = os.environ.copy()
    env["QA_ROOT"] = str(qa)
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, str(BOX_HEALTH)],
        cwd=tmp,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    check(result.returncode == 0, f"本机体检退出码应是 0，实际 {result.returncode}")
    check("SwapFree" in result.stdout, "本机体检没有 SwapFree")
    check("退出码 10" not in result.stdout, "本机体检仍在说退出码 10")


def test_html_report(tmp: Path) -> None:
    batch = tmp / "batch"
    batch.mkdir()
    (batch / "step.png").write_bytes(tiny_png())
    secret = "example-secret-value"
    rows = [
        {
            "id": "DEMO-1",
            "title": "示例",
            "result": "失败",
            "summary": f"密码={secret}",
            "password": secret,
            "shots": [{"file": "step.png", "caption": "红框标出按钮", "box": [1, 2, 3, 4]}],
        },
        {
            "id": "DEMO-2",
            "title": "范围外",
            "result": "通过",
            "summary": "Bearer should-not-leak",
            "screenshot": "/etc/hosts",
        },
    ]
    source = batch / "results.jsonl"
    source.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, str(HTML_REPORT)],
        cwd=batch,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    check(result.returncode == 0, f"html_report 退出码 {result.returncode}: {result.stderr}")
    report = (batch / "report.html").read_text(encoding="utf-8")
    check("data:image/png;base64," in report, "报告没有内嵌 png")
    check("left:1px;top:2px;width:3px;height:4px" in report, "红框坐标没有写进报告")
    check("红框标出按钮" in report, "白话说明不在图旁")
    check(secret not in report, "报告里仍有密钥")
    check("should-not-leak" not in report, "报告里仍有 Bearer 后面的值")
    check("密码=***" in report and "Bearer ***" in report, "脱敏替换不完整")
    check(report.count("data:image") == 1, "范围外的文件不应被嵌进报告")
    check("<script" not in report and "http://" not in report and "https://" not in report, "报告引用了外链或脚本")
    check("通过 1，失败 1" in result.stdout, "stdout 没有计数")

    missing = subprocess.run(
        [sys.executable, str(HTML_REPORT), str(tmp / "missing.jsonl")],
        cwd=tmp,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    check(missing.returncode == 2, "找不到结果文件时应返回 2")
    secret_dir = tmp / "secrets"
    secret_dir.mkdir()
    blocked = subprocess.run(
        [sys.executable, str(HTML_REPORT), str(source), "-o", str(secret_dir / "report.html")],
        cwd=batch,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    check(blocked.returncode == 2, "不应把报告写进 secrets")
    check(not (secret_dir / "report.html").exists(), "secrets 目录里出现了报告")


def executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def test_qa_ready(tmp: Path) -> None:
    home = tmp / "home"
    qa = tmp / "qa"
    venv_bin = home / ".venvs" / "qa" / "bin"
    cache = home / ".cache" / "ms-playwright" / "chromium-test"
    stubs = tmp / "stubs"
    for path in (venv_bin, cache, stubs, qa / "bin"):
        path.mkdir(parents=True)
    executable(
        venv_bin / "python",
        "#!/bin/sh\ncase \"$*\" in\n  *pyotp*) exit 1 ;;\nesac\nexit 0\n",
    )
    os.symlink(venv_bin / "python", venv_bin / "pytest")
    os.symlink(venv_bin / "python", venv_bin / "playwright")
    pip_log = tmp / "pip.log"
    npm_log = tmp / "npm.log"
    called = tmp / "called.log"
    executable(venv_bin / "pip", f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> '{pip_log}'\nexit 0\n")
    executable(stubs / "npm", f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> '{npm_log}'\nexit 0\n")
    for name in ("apt", "apt-get", "sudo", "bootstrap_bot_computer.sh"):
        executable(stubs / name, f"#!/bin/sh\nprintf '%s\\n' {name} >> {called}\nexit 99\n")
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "QA_ROOT": str(qa),
            "VENV": str(home / ".venvs" / "qa"),
            "REPO_DIR": str(tmp / "empty-repo"),
            "PATH": f"{stubs}:/usr/bin:/bin",
            "LANG": "C.UTF-8",
        }
    )
    first = subprocess.run([str(QA_READY)], cwd=tmp, env=env, capture_output=True, text=True, check=False)
    check(first.returncode == 0, f"qa-ready 首次退出码 {first.returncode}\n{first.stdout}\n{first.stderr}")
    check("qa-ready: ok" in first.stdout, "qa-ready 没有打印 ok")
    check("bin=yes" in first.stdout, "PATH 里没有 qa/bin")
    check("playwright-cli=no" in first.stdout and "agent-browser=no" in first.stdout, "不存在的命令被当成已安装")
    pip_text = pip_log.read_text(encoding="utf-8") if pip_log.exists() else ""
    npm_text = npm_log.read_text(encoding="utf-8") if npm_log.exists() else ""
    check("pyotp=no" in first.stdout, "pyotp 还没装上时状态行不应写成 yes")
    check("install pyotp" in pip_text and "-r" not in pip_text, f"pyotp 安装命令不对：{pip_text!r}")
    check("@playwright/cli@latest" in npm_text, f"没有记下 playwright-cli 安装命令：{npm_text!r}")
    check("agent-browser" in npm_text, f"没有记下 agent-browser 安装命令：{npm_text!r}")
    check("--prefix" in npm_text and str(home / ".local") in npm_text, "npm 安装没有装到用户目录")
    check(not called.exists(), "qa-ready 调用了 apt、sudo 或 bootstrap")
    bashrc = (home / ".bashrc").read_text(encoding="utf-8")
    check(bashrc.count("# qa-ready") == 1, "PATH 行没有写入 bashrc")
    check(not (home / ".profile").exists(), "不应新建 .profile")

    second = subprocess.run([str(QA_READY)], cwd=tmp, env=env, capture_output=True, text=True, check=False)
    check(second.returncode == 0, "qa-ready 第二次应成功")
    check((home / ".bashrc").read_text(encoding="utf-8").count("# qa-ready") == 1, "PATH 行被重复写入")

    marker = tmp / "health-marker"
    (qa / "bin" / "box_health.py").write_text(
        "import os, sys\n"
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text(' '.join(sys.argv[1:]))\n"
        "raise SystemExit(10)\n",
        encoding="utf-8",
    )
    plain = subprocess.run([str(QA_READY)], cwd=tmp, env=env, capture_output=True, text=True, check=False)
    check(plain.returncode == 0 and not marker.exists(), "默认开工不应跑体检")
    health = subprocess.run([str(QA_READY), "--health"], cwd=tmp, env=env, capture_output=True, text=True, check=False)
    check(health.returncode == 0, f"--health 不应因体检退出码 10 而失败：{health.returncode}")
    check(marker.exists() and marker.read_text(encoding="utf-8") == "", "--health 没有调用体检")
    marker.unlink()
    clean = subprocess.run([str(QA_READY), "--clean"], cwd=tmp, env=env, capture_output=True, text=True, check=False)
    check(clean.returncode == 0, "--clean 不应失败")
    check(marker.read_text(encoding="utf-8") == "--clean", "--clean 没有把参数传给体检")


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        test_box_health(tmp)
        test_live_proc(tmp)
        test_html_report(tmp)
        test_qa_ready(tmp)
    if FAILURES:
        print("\n".join(FAILURES), file=sys.stderr)
        return 1
    print("check_backup: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
