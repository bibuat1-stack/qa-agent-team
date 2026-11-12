#!/usr/bin/env bash
# 云电脑工具链检查。这是仓库备份，云电脑上的运行位置是 /workspace/qa/qa-ready.sh。
# 不跑 apt，不调用 bootstrap_bot_computer.sh，不改平台桌面 Chrome、8791 代理或 Xvfb。
# 安装失败时把最后 30 行追加到 $QA_ROOT/runs/bootstrap-error.log，然后继续，退出码仍为 0。
# 默认不跑内存体检。开工技能只在需要时加 --health；--clean 才做租约和临时配置清理。
# 体检本身失败也不改变本脚本的退出码。
#
# 缺了才执行的安装命令（不走 apt）：
#   "$VENV/bin/pip" install pyotp
#   npm install -g --prefix "$HOME/.local" @playwright/cli@latest
#   npm install -g --prefix "$HOME/.local" agent-browser
set -euo pipefail

QA_ROOT="${QA_ROOT:-/workspace/qa}"
REPO_DIR="${REPO_DIR:-$QA_ROOT/repo}"
VENV="${VENV:-$HOME/.venvs/qa}"
LOG="$QA_ROOT/runs/bootstrap-error.log"

export PATH="$HOME/.local/bin:$QA_ROOT/bin:$PATH"

mkdir -p "$QA_ROOT/runs" "$QA_ROOT/bin" "$HOME/.local/bin"

persist_path() {
  # 当前进程的 PATH 上面已经导出。这里再给以后的交互式 shell 留一行。
  # 不新建 ~/.profile，避免变成该用户的第一份登录配置。
  local rc line
  line="export PATH=\"\$HOME/.local/bin:${QA_ROOT}/bin:\$PATH\" # qa-ready"
  [ -f "$HOME/.bashrc" ] || touch "$HOME/.bashrc" || return 0
  for rc in "$HOME/.bashrc" "$HOME/.profile" "$HOME/.bash_profile"; do
    [ -f "$rc" ] || continue
    if grep -Fqs "# qa-ready" "$rc"; then
      continue
    fi
    printf '\n%s\n' "$line" >> "$rc" || true
  done
}

run_or_log() {
  local tmp status
  tmp=$(mktemp)
  set +e
  "$@" >"$tmp" 2>&1
  status=$?
  set -e
  if [ "$status" -ne 0 ]; then
    mkdir -p "$(dirname "$LOG")"
    tail -n 30 "$tmp" >> "$LOG"
    echo "qa-ready: failed ($status): $* ; last 30 lines in $LOG" >&2
  fi
  rm -f "$tmp"
  return 0
}

usage() {
  cat <<'EOF'
用法: qa-ready.sh [--health] [--clean]
检查 pytest、Chromium、pyotp、playwright-cli、agent-browser，并把 /workspace/qa/bin 放进 PATH。
不跑 apt。缺 pytest 才安装仓库 requirements；缺 Chromium 只执行 playwright install chromium。
--health  额外运行 box_health.py（不加 --clean）。失败不影响退出码。
--clean   额外运行 box_health.py --clean。失败不影响退出码。
EOF
}

RUN_HEALTH=0
RUN_CLEAN=0
for arg in "$@"; do
  case "$arg" in
    --help|-h) usage; exit 0 ;;
    --health) RUN_HEALTH=1 ;;
    --clean) RUN_CLEAN=1; RUN_HEALTH=1 ;;
  esac
done

persist_path

if [ ! -x "$VENV/bin/pytest" ]; then
  python3 -m venv "$VENV"
  run_or_log "$VENV/bin/python" -m pip install --upgrade pip
  if [ -f "$REPO_DIR/requirements.txt" ]; then
    run_or_log "$VENV/bin/pip" install -r "$REPO_DIR/requirements.txt"
  fi
fi

if [ -x "$VENV/bin/python" ] && ! "$VENV/bin/python" -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
  if [ -f "$REPO_DIR/requirements.txt" ]; then
    run_or_log "$VENV/bin/pip" install -r "$REPO_DIR/requirements.txt"
  else
    run_or_log "$VENV/bin/pip" install playwright
  fi
fi

if [ -x "$VENV/bin/playwright" ] && ! ls -d "$HOME/.cache/ms-playwright"/chromium-* >/dev/null 2>&1; then
  # 不要加 --with-deps，那会走 apt。
  run_or_log "$VENV/bin/playwright" install chromium
fi

if [ -x "$VENV/bin/python" ] && ! "$VENV/bin/python" -c "import pyotp" 2>/dev/null; then
  if [ -x "$VENV/bin/pip" ]; then
    run_or_log "$VENV/bin/pip" install pyotp
  else
    echo "qa-ready: pip missing, skip pyotp" >> "$LOG"
  fi
fi

if ! command -v playwright-cli >/dev/null 2>&1; then
  if command -v npm >/dev/null 2>&1; then
    run_or_log npm install -g --prefix "$HOME/.local" @playwright/cli@latest
  else
    echo "qa-ready: npm missing, skip playwright-cli" >> "$LOG"
  fi
fi

if ! command -v agent-browser >/dev/null 2>&1; then
  if command -v npm >/dev/null 2>&1; then
    run_or_log npm install -g --prefix "$HOME/.local" agent-browser
  else
    echo "qa-ready: npm missing, skip agent-browser" >> "$LOG"
  fi
fi

if [ "$RUN_HEALTH" -eq 1 ] && [ -f "$QA_ROOT/bin/box_health.py" ]; then
  if [ "$RUN_CLEAN" -eq 1 ]; then
    python3 "$QA_ROOT/bin/box_health.py" --clean || true
  else
    python3 "$QA_ROOT/bin/box_health.py" || true
  fi
fi

py_ok=no
otp_ok=no
chr_ok=no
cli_ok=no
ab_ok=no
bin_ok=no
if [ -x "$VENV/bin/pytest" ]; then
  py_ok=yes
fi
if [ -x "$VENV/bin/python" ] && "$VENV/bin/python" -c "import pyotp" 2>/dev/null; then
  otp_ok=yes
fi
if ls -d "$HOME/.cache/ms-playwright"/chromium-* >/dev/null 2>&1; then
  chr_ok=yes
fi
if command -v playwright-cli >/dev/null 2>&1; then
  cli_ok=yes
fi
if command -v agent-browser >/dev/null 2>&1; then
  ab_ok=yes
fi
case ":$PATH:" in
  *":$QA_ROOT/bin:"*) bin_ok=yes ;;
esac

echo "qa-ready: pytest=$py_ok chromium=$chr_ok pyotp=$otp_ok playwright-cli=$cli_ok agent-browser=$ab_ok bin=$bin_ok"
echo "qa-ready: ok"
