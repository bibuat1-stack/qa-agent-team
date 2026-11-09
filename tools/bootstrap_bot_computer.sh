#!/usr/bin/env bash
# Rebuild the test toolchain on the Grok Bot cloud computer.
# Installed packages, virtualenvs, and browsers do not survive a computer update,
# Recover, or Reset, so run this at the start of every test session. Safe to rerun.
set -euo pipefail

REPO_URL="${1:?usage: bootstrap_bot_computer.sh <repo-url> [branch]}"
BRANCH="${2:-main}"
QA_ROOT="${QA_ROOT:-/workspace/qa}"
REPO_DIR="$QA_ROOT/repo"
VENV="${VENV:-$HOME/.venvs/qa}"

need() { command -v "$1" >/dev/null 2>&1; }

mkdir -p "$QA_ROOT/requirements" "$QA_ROOT/runs" "$QA_ROOT/escalations" "$QA_ROOT/triage"

missing=()
need git || missing+=(git)
need python3 || missing+=(python3)
python3 -c 'import venv, ensurepip' 2>/dev/null || missing+=(python3-venv python3-pip)
if [ "${#missing[@]}" -gt 0 ]; then
  sudo apt-get update -y
  sudo apt-get install -y "${missing[@]}"
fi
need gh || { sudo apt-get install -y gh || echo "gh is not in apt; see https://cli.github.com for install steps"; }

if [ -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" fetch --prune origin
  git -C "$REPO_DIR" checkout "$BRANCH"
  git -C "$REPO_DIR" pull --ff-only origin "$BRANCH"
else
  git clone --branch "$BRANCH" "$REPO_URL" "$REPO_DIR"
fi

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/pip" install -r "$REPO_DIR/requirements.txt"
"$VENV/bin/python" -m playwright install --with-deps chromium

if [ "${INSTALL_CURSOR_CLI:-0}" = "1" ] && ! need agent; then
  curl https://cursor.com/install -fsS | bash
fi

echo "ready: source $VENV/bin/activate && cd $REPO_DIR"
