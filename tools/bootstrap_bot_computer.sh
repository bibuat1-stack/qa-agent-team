#!/usr/bin/env bash
# Rebuild the test toolchain on the Grok Bot cloud computer.
# Packages, virtualenvs, and browsers do not survive a computer update, Recover,
# or Reset. Run this at the start of every test session; it is safe to rerun.
# When the requirements hash and Chromium are already in place, pip and browser
# downloads are skipped.
set -euo pipefail

export GIT_TERMINAL_PROMPT=0
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_NO_INPUT=1

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  echo "usage: bootstrap_bot_computer.sh <repo-url> [branch]"
  exit 0
fi

REPO_URL="${1:?usage: bootstrap_bot_computer.sh <repo-url> [branch]}"
BRANCH="${2:-main}"
QA_ROOT="${QA_ROOT:-/workspace/qa}"
REPO_DIR="$QA_ROOT/repo"
VENV="${VENV:-$HOME/.venvs/qa}"
PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"
export PLAYWRIGHT_BROWSERS_PATH
STAMP="$VENV/.qa-toolchain-stamp"
KEEP_DAYS="${QA_KEEP_RUN_DAYS:-7}"
START_EPOCH=$(date +%s)

need() { command -v "$1" >/dev/null 2>&1; }

pkg_installed() {
  dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"
}

browser_libs_ok() {
  pkg_installed libnss3 && pkg_installed libnspr4 && pkg_installed libgbm1 && pkg_installed libxkbcommon0 \
    && { pkg_installed libatk-bridge2.0-0 || pkg_installed libatk-bridge2.0-0t64; }
}

needs_browser() {
  [ -f "$REPO_DIR/requirements.txt" ] && grep -Eiq '(^|[[:space:]])pytest-playwright([<>=!~[:space:]]|$)' "$REPO_DIR/requirements.txt"
}

mkdir -p "$QA_ROOT/requirements" "$QA_ROOT/runs" "$QA_ROOT/escalations" "$QA_ROOT/triage"
exec 9>"$QA_ROOT/.bootstrap.lock"
if ! flock -w 600 9; then
  echo "bootstrap 等待锁超过 600 秒。同一台云电脑不要并行执行 bootstrap。" >&2
  exit 1
fi

missing=()
need git || missing+=(git)
need python3 || missing+=(python3)
python3 -c 'import venv, ensurepip' 2>/dev/null || missing+=(python3-venv python3-pip)
if [ "${#missing[@]}" -gt 0 ]; then
  sudo apt-get update -y
  sudo apt-get install -y "${missing[@]}"
fi
# gh 只在开 GitHub issue 时需要。默认不跑 apt，避免每次会话都更新软件源。
if ! need gh; then
  if [ "${QA_INSTALL_GH:-0}" = "1" ]; then
    sudo apt-get install -y gh || echo "gh is not in apt; see https://cli.github.com for install steps"
  else
    echo "gh 未安装（测试不需要）。需要时再执行 QA_INSTALL_GH=1 bash tools/bootstrap_bot_computer.sh ..."
  fi
fi

if [ -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" fetch --prune --no-tags origin "$BRANCH"
  git -C "$REPO_DIR" checkout "$BRANCH"
  git -C "$REPO_DIR" pull --ff-only origin "$BRANCH"
else
  git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$REPO_DIR"
fi

req_hash=$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$REPO_DIR/requirements.txt")
py_ver=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')

imports_ok() {
  REPO_DIR="$REPO_DIR" "$VENV/bin/python" - <<'PY'
import os
import re
import sys
from pathlib import Path

text = Path(os.environ["REPO_DIR"], "requirements.txt").read_text(encoding="utf-8")
mapping = {
    "pytest": "pytest",
    "requests": "requests",
    "allure-pytest": "allure",
    "pytest-html": "pytest_html",
    "pytest-rerunfailures": "pytest_rerunfailures",
    "pytest-playwright": "pytest_playwright",
    "pytest-xdist": "xdist",
    "python-dotenv": "dotenv",
    "pyyaml": "yaml",
}
modules = []
for line in text.splitlines():
    line = line.split("#", 1)[0].strip()
    if not line or line.startswith("-"):
        continue
    name = re.split(r"[<>=!~\[]", line, maxsplit=1)[0].strip().replace("_", "-").lower()
    if name in mapping:
        modules.append(mapping[name])
if not modules:
    sys.exit(0)
try:
    exec("import " + ",".join(modules), {})  # noqa: S102 — 固定映射，不是外部字符串
except Exception:
    sys.exit(1)
PY
}

browser_ok() {
  "$VENV/bin/python" - <<'PY'
import os
import sys

from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()
try:
    executable = playwright.chromium.executable_path
finally:
    playwright.stop()
sys.exit(0 if os.path.isfile(executable) and os.access(executable, os.X_OK) else 1)
PY
}

toolchain_ready() {
  [ -x "$VENV/bin/python" ] || return 1
  [ -f "$STAMP" ] || return 1
  grep -Fqx "python=$py_ver" "$STAMP" || return 1
  grep -Fqx "requirements=$req_hash" "$STAMP" || return 1
  imports_ok || return 1
  if needs_browser; then
    grep -Fqx "browser=ok" "$STAMP" || return 1
    browser_libs_ok || return 1
    browser_ok || return 1
  fi
}

write_stamp() {
  {
    echo "python=$py_ver"
    echo "requirements=$req_hash"
    if needs_browser; then
      echo "browser=ok"
    fi
  } >"$STAMP"
}

install_toolchain() {
  if [ ! -x "$VENV/bin/python" ]; then
    python3 -m venv "$VENV"
  fi
  if ! "$VENV/bin/python" -m pip install -r "$REPO_DIR/requirements.txt"; then
    "$VENV/bin/python" -m pip install --upgrade pip
    "$VENV/bin/python" -m pip install -r "$REPO_DIR/requirements.txt"
  fi
  if needs_browser; then
    if ! browser_libs_ok; then
      "$VENV/bin/python" -m playwright install-deps chromium
    fi
    "$VENV/bin/python" -m playwright install chromium
  fi
  write_stamp
}

MODE="cached"
if ! toolchain_ready; then
  MODE="installed"
  install_toolchain
fi

reap_orphan_browsers() {
  local pid comm exe ppid
  for pid_dir in /proc/[0-9]*; do
    pid=${pid_dir#/proc/}
    comm=$(cat "$pid_dir/comm" 2>/dev/null || true)
    case "$comm" in
      chrome|chromium|headless_shell|chrome-headless-shell) ;;
      *) continue ;;
    esac
    exe=$(readlink -f "$pid_dir/exe" 2>/dev/null || true)
    case "$exe" in
      *ms-playwright*) ;;
      *) continue ;;
    esac
    ppid=$(awk '{print $4}' "$pid_dir/stat" 2>/dev/null || true)
    if [ "$ppid" = "1" ]; then
      kill "$pid" 2>/dev/null || true
      echo "reaped orphan browser pid=$pid"
    fi
  done
}

housekeep() {
  local free_kb days
  days=$KEEP_DAYS
  free_kb=$(df -Pk "$QA_ROOT" | awk 'NR==2 {print $4}')
  if [ "${free_kb:-0}" -lt 2097152 ]; then
    days=2
    echo "disk free < 2GB, pruning runs older than ${days} days"
  fi
  if [ -d "$QA_ROOT/runs" ]; then
    find "$QA_ROOT/runs" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended \
      -regex '.*/[0-9]{8}-[0-9]{4,6}(-[0-9]+)?$' -mtime +"$days" -print -exec rm -rf {} +
  fi
  local dir
  for dir in "$REPO_DIR/reports" "$REPO_DIR/logs" "$REPO_DIR/test-results"; do
    [ -d "$dir" ] || continue
    find "$dir" -mindepth 1 ! -name '.gitkeep' -mtime +"$days" -delete
  done
  if [ "${QA_SKIP_REAP:-0}" != "1" ]; then
    reap_orphan_browsers
  fi
}

if [ "${QA_SKIP_HOUSEKEEP:-0}" != "1" ]; then
  housekeep || echo "housekeep failed, continuing"
fi

cat >"$QA_ROOT/cloud.env" <<EOF
QA_CLOUD=1
PIP_DISABLE_PIP_VERSION_CHECK=1
PIP_NO_INPUT=1
PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_BROWSERS_PATH
EOF
chmod 600 "$QA_ROOT/cloud.env"

if [ "${INSTALL_CURSOR_CLI:-0}" = "1" ] && ! need agent; then
  curl https://cursor.com/install -fsS | bash
fi

mem_line=$(awk '/MemAvailable/ {printf "%dMB", $2/1024}' /proc/meminfo 2>/dev/null || echo "unknown")
disk_line=$(df -hP "$QA_ROOT" | awk 'NR==2 {print $4 " free"}')
elapsed=$(( $(date +%s) - START_EPOCH ))
echo "ready: source $VENV/bin/activate && cd $REPO_DIR"
echo "toolchain=$MODE bootstrap_seconds=$elapsed resources: mem_available=$mem_line disk=$disk_line"
echo "next: bash tools/run_cloud.sh --suite api -m smoke"
