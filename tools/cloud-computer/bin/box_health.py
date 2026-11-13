#!/usr/bin/env python3
"""云电脑体检：记下内存被谁占用，只做不会误伤的清理。

用法：
  python3 box_health.py            只体检，不改任何东西
  python3 box_health.py --clean    体检，并删除作废的租约和没人在用的临时浏览器配置

每次运行往 <QA_ROOT>/runs/box-health/health.jsonl 追加一行，摘要写到同目录 latest.md。
退出码始终是 0。可用内存低于提示门槛（默认 2048 MiB）时，只在摘要里提示总控，
不拦截开工、开浏览器或收尾，也不排队等待。每次另记 SwapFree。

不结束任何进程。命令行参数只用来分类，不写进输出；环境变量只读 DISPLAY 和 QA_OWNER。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

PROC = Path(os.environ.get("BOX_PROC", "/proc"))
TMP = Path(os.environ.get("BOX_TMP", "/tmp"))
QA_ROOT = Path(os.environ.get("QA_ROOT", "/workspace/qa"))
OUT_DIR = QA_ROOT / "runs" / "box-health"
LEASE_DIR = QA_ROOT / "leases"

# 2048 MiB 只用于提示总控。不要改回按内存返回非 0，也不要在开浏览器前排队等待。
HINT_AVAIL_MIB = 2048
LEASE_STALE_HOURS = 2    # 租约有效期 30 分钟；2 小时没续期按作废处理
PROFILE_STALE_HOURS = 1  # 临时浏览器配置：没有进程引用，且 1 小时没动过
BROWSER_OLD_HOURS = 2    # 自启浏览器开了这么久，列为「疑似忘关」
BROWSER_MIN_MIB = 50     # 整棵进程树小于这个数的不列

TZ = dt.timezone(dt.timedelta(hours=8))
PLAYWRIGHT_BROWSER = "自启 Chromium（Playwright）"
AGENT_BROWSER = "agent-browser（含它的 Chrome）"
SELF_BROWSERS = (PLAYWRIGHT_BROWSER, AGENT_BROWSER)
DESKTOP_PREFIXES = ("Xvfb", "x11vnc", "xfce", "xfwm", "xfdesktop", "exec-daemon", "picom", "pulseaudio", "dbus")
SCRIPT_ARG = re.compile(r"[\w./@+-]+\.(?:js|mjs|cjs|ts|py)")
MODULE_ARG = re.compile(r"[\w.]+")


def hint_avail_mib() -> int:
    """提示门槛。BOX_HINT_AVAIL_MIB 只改文案里的数字，不改退出码。"""
    raw = os.environ.get("BOX_HINT_AVAIL_MIB", str(HINT_AVAIL_MIB))
    try:
        value = int(raw)
    except ValueError:
        return HINT_AVAIL_MIB
    if value < 0:
        return HINT_AVAIL_MIB
    return value


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def link(path: Path) -> str:
    try:
        return os.readlink(path)
    except OSError:
        return ""


def base(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def stamp() -> str:
    return dt.datetime.now(TZ).isoformat(timespec="seconds")


def meminfo() -> dict[str, float]:
    """/proc/meminfo，单位换成 MiB。"""
    out = {}
    for line in read(PROC / "meminfo").splitlines():
        key, _, rest = line.partition(":")
        parts = rest.split()
        if parts and parts[0].isdigit():
            out[key] = int(parts[0]) / 1024
    return out


def pss_mib(pid_dir: Path) -> float:
    for line in read(pid_dir / "smaps_rollup").splitlines():
        if line.startswith("Pss:"):
            return int(line.split()[1]) / 1024
    for line in read(pid_dir / "status").splitlines():  # 读不到 Pss 时退回 RSS
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1024
    return 0.0


def processes() -> list[dict]:
    uptime = float((read(PROC / "uptime").split() or ["0"])[0])
    ticks = os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else 100
    procs = []
    for pid_dir in PROC.iterdir():
        if not pid_dir.name.isdigit():
            continue
        stat = read(pid_dir / "stat")
        if ")" not in stat:
            continue
        fields = stat.rsplit(")", 1)[1].split()  # fields[1] 是父进程号，fields[19] 是启动时刻
        if len(fields) < 20:
            continue
        argv = [arg for arg in read(pid_dir / "cmdline").split("\0") if arg]
        env = dict(item.split("=", 1) for item in read(pid_dir / "environ").split("\0") if "=" in item)
        exe = link(pid_dir / "exe") or (argv[0] if argv else "")
        procs.append(
            {
                "pid": int(pid_dir.name),
                "ppid": int(fields[1]),
                "name": read(pid_dir / "comm").strip() or base(exe),
                "exe": exe,
                "argv": argv,  # 只在内存里用于分类和判断配置目录是否在用，不写进任何输出
                "pss": pss_mib(pid_dir),
                "age_h": max(0.0, uptime - int(fields[19]) / ticks) / 3600,
                "display": env.get("DISPLAY", ""),
                "owner": env.get("QA_OWNER", ""),
                "cwd": link(pid_dir / "cwd"),
            }
        )
    return procs


def label(name: str, argv: list[str]) -> str:
    """程序名。node 和 python 再带上脚本文件名或模块名，其他参数一律不带。"""
    if name.startswith(("node", "python")):
        head = argv[1:8]
        for i, arg in enumerate(head):
            if arg == "-m" and i + 1 < len(head) and MODULE_ARG.fullmatch(head[i + 1]):
                return f"{name} -m {head[i + 1]}"
            if SCRIPT_ARG.fullmatch(arg):
                return f"{name} {base(arg)}"
    return name


def kind(p: dict) -> str:
    """把进程归类，用于汇总。"""
    exe, name = p["exe"], p["name"]
    if "ms-playwright" in exe:
        return PLAYWRIGHT_BROWSER
    if ".agent-browser" in exe:
        return AGENT_BROWSER
    if "chrom" in name.lower() or "chrom" in base(exe).lower():
        return "其他 Chrome（含平台桌面 Chrome）"
    if name.startswith(DESKTOP_PREFIXES):
        return "桌面服务"
    return label(name, p["argv"])


def owner(p: dict) -> str:
    """优先用 QA_OWNER；没有就用 /workspace 下的项目目录名做线索。"""
    if p["owner"]:
        return p["owner"]
    parts = p["cwd"].split("/")
    if len(parts) > 2 and parts[1] == "workspace":
        return f"目录 {parts[2]}"
    return "未标记"


def sums(procs: list[dict], key) -> list[list]:
    """按 key 汇总，返回 [名称, 进程数, Pss MiB]，从大到小。"""
    acc: dict = defaultdict(lambda: [0, 0.0])
    for p in procs:
        item = acc[key(p)]
        item[0] += 1
        item[1] += p["pss"]
    return sorted(([name, n, round(mib)] for name, (n, mib) in acc.items()), key=lambda row: -row[2])


def tree_pss(root: int, children: dict[int, list[int]], by_pid: dict[int, dict]) -> float:
    total, stack = 0.0, [root]
    while stack:
        pid = stack.pop()
        total += by_pid[pid]["pss"]
        stack.extend(children.get(pid, []))
    return total


def tmpfs_mib() -> dict[str, int]:
    """tmpfs 里的文件占的是内存。返回各挂载点已用 MiB。"""
    used: dict[str, int] = {}
    if not hasattr(os, "statvfs"):
        return used
    for line in read(PROC / "mounts").splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[2] == "tmpfs":
            try:
                st = os.statvfs(parts[1])
            except OSError:
                continue
            used[parts[1]] = round((st.f_blocks - st.f_bfree) * st.f_frsize / 2**20)
    return used


def older_than(path: Path, hours: float) -> bool:
    try:
        return time.time() - path.stat().st_mtime > hours * 3600
    except OSError:
        return False


def dir_mib(path: Path) -> float:
    total = 0
    for root, _, files in os.walk(path):
        for name in files:
            try:
                total += os.lstat(os.path.join(root, name)).st_size
            except OSError:
                pass
    return total / 2**20


def clean(all_procs: list[dict]) -> dict:
    """只删两类东西：作废的租约文件，没有进程引用的临时浏览器配置。"""
    done: dict = {"leases": [], "profiles": [], "freed_mib": 0}
    if LEASE_DIR.is_dir():
        for lease in LEASE_DIR.glob("*.json"):
            if older_than(lease, LEASE_STALE_HOURS):
                lease.unlink(missing_ok=True)
                done["leases"].append(lease.name)
        if done["leases"]:
            with (LEASE_DIR / "log.jsonl").open("a", encoding="utf-8") as log:
                entry = {"at": stamp(), "by": "box_health", "removed_stale": done["leases"]}
                log.write(json.dumps(entry, ensure_ascii=False) + "\n")
    in_use = "\0".join(arg for p in all_procs for arg in p["argv"])
    freed = 0.0
    for profile in TMP.glob("playwright_*profile-*"):
        if profile.is_dir() and profile.name not in in_use and older_than(profile, PROFILE_STALE_HOURS):
            freed += dir_mib(profile)
            shutil.rmtree(profile, ignore_errors=True)
            done["profiles"].append(profile.name)
    done["freed_mib"] = round(freed)
    return done


def table(headers: list[str], rows: list[list]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    return lines + ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description="云电脑体检；加 --clean 时做两种不会误伤的清理。不结束任何进程。")
    parser.add_argument("--clean", action="store_true", help="删除作废的租约和没人在用的临时浏览器配置")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    mem = meminfo()
    hint = hint_avail_mib()
    all_procs = processes()
    procs = [p for p in all_procs if p["pss"] > 0]
    for p in procs:
        p["kind"], p["who"] = kind(p), owner(p)
    by_pid = {p["pid"]: p for p in procs}
    children: dict[int, list[int]] = defaultdict(list)
    for p in procs:
        children[p["ppid"]].append(p["pid"])

    forgotten = []
    for p in procs:
        parent = by_pid.get(p["ppid"])
        is_child = parent is not None and parent["kind"] == p["kind"]
        if p["kind"] not in SELF_BROWSERS or is_child or p["age_h"] < BROWSER_OLD_HOURS:
            continue
        size = tree_pss(p["pid"], children, by_pid)
        if size >= BROWSER_MIN_MIB:
            mode = "无头" if any(arg.startswith("--headless") for arg in p["argv"]) else "有头"
            forgotten.append([p["pid"], p["kind"], mode, round(size), f"{p['age_h']:.1f}", p["display"] or "—", p["who"]])

    displays = sorted(
        {arg for p in procs if p["name"] == "Xvfb" for arg in p["argv"][1:2] if arg.startswith(":")},
        key=lambda d: int(d[1:]) if d[1:].isdigit() else 0,
    )
    top = sorted(procs, key=lambda p: -p["pss"])[:15]
    top_rows = [
        [p["pid"], p["kind"], round(p["pss"]), f"{p['age_h']:.1f}", p["display"] or "—", p["who"], p["cwd"] or "—"]
        for p in top
    ]
    by_kind = sums(procs, lambda p: p["kind"])[:12]
    by_display = sums(procs, lambda p: p["display"] or "无显示号")[:10]
    by_owner = sums(procs, lambda p: p["who"])[:10]
    tmpfs = tmpfs_mib()
    cleaned = clean(all_procs) if args.clean else None

    avail, total = round(mem.get("MemAvailable", 0)), round(mem.get("MemTotal", 0))
    low = avail < hint
    swap_free = round(mem["SwapFree"]) if "SwapFree" in mem else None
    swap_free_text = "未读到" if swap_free is None else f"{swap_free} MiB"
    state = "低于门槛，只提示总控，不拦截任何操作" if low else "未低于门槛"
    load1 = (read(PROC / "loadavg").split() or ["?"])[0]
    now = stamp()

    lines = [
        f"# 云电脑体检 {now}",
        "",
        f"可用内存 {avail} MiB，共 {total} MiB。提示门槛 {hint} MiB，{state}。"
        f"SwapFree {swap_free_text}。1 分钟负载 {load1}。"
        f"tmpfs 占用 {sum(tmpfs.values())} MiB，共享内存 {round(mem.get('Shmem', 0))} MiB。"
        f"显示号：{' '.join(displays) or '无'}。",
        "",
        "## 内存按程序（Pss）",
        *table(["程序", "进程数", "MiB"], by_kind),
        "",
        "## 内存按显示号",
        *table(["显示号", "进程数", "MiB"], by_display),
        "",
        "## 内存按号（QA_OWNER，没有时用工作目录）",
        *table(["号", "进程数", "MiB"], by_owner),
        "",
        "## 占用最多的 15 个进程",
        *table(["pid", "程序", "MiB", "已运行小时", "显示号", "号", "工作目录"], top_rows),
    ]
    if forgotten:
        lines += [
            "",
            f"## 疑似忘关的自启浏览器（开了 {BROWSER_OLD_HOURS} 小时以上，只列不关）",
            *table(["pid", "程序", "模式", "整棵树 MiB", "已运行小时", "显示号", "号"], forgotten),
        ]
    if cleaned is not None:
        lines += [
            "",
            "## 本次清理",
            f"作废租约 {len(cleaned['leases'])} 个；临时浏览器配置 {len(cleaned['profiles'])} 个，约 {cleaned['freed_mib']} MiB。",
        ]
    if low:
        lines += ["", f"提示总控：可用内存低于 {hint} MiB。只提示，不拦截，退出码 0。"]

    record = {
        "at": now,
        "avail_mib": avail,
        "total_mib": total,
        "shmem_mib": round(mem.get("Shmem", 0)),
        "swap_mib": round(mem.get("SwapTotal", 0)),
        "swap_free_mib": swap_free,
        "hint_avail_mib": hint,
        "low_memory": low,
        "blocks_operation": False,
        "load1": load1,
        "displays": displays,
        "tmpfs_mib": tmpfs,
        "by_kind": by_kind,
        "by_display": by_display,
        "by_owner": by_owner,
        "top": top_rows,
        "forgotten": forgotten,
        "cleaned": cleaned,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (OUT_DIR / "health.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps(record, ensure_ascii=False) + "\n")
    (OUT_DIR / "latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
