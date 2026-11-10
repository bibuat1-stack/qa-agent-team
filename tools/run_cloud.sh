#!/usr/bin/env bash
# Run pytest on the Grok Bot cloud computer with a memory cap, no hidden reruns,
# and a summary.json the next bot can read without pasting logs into chat.
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
export TZ=Asia/Taipei
export PYTHONPATH="$REPO_DIR${PYTHONPATH:+:$PYTHONPATH}"

usage() {
  cat <<'EOF'
usage: run_cloud.sh [--suite api|ui|all] [--env NAME] [-m EXPR] [--reruns N] [--workers N] [--dry-run] [-- <pytest args>]

默认失败不重跑，按可用内存决定并发。UI 只在失败时留截图和 trace，不录视频。
可用内存低于 800MB 时不启动浏览器，该套件记为未跑，不能当成通过。
结果写到 $QA_ROOT/runs/<YYYYMMDD-HHMMSS>/summary.json（时间是 Asia/Taipei）。
先结论后证据：把 summary.txt 交回去，不要把日志全文贴进聊天。
EOF
}

SUITE="all"
ENV_NAME=""
MARKERS=""
RERUNS="0"
WORKERS=""
DRY_RUN=0
EXTRA=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --suite) SUITE="$2"; shift 2 ;;
    --env) ENV_NAME="$2"; shift 2 ;;
    -m|--markers) MARKERS="$2"; shift 2 ;;
    --reruns) RERUNS="$2"; shift 2 ;;
    --workers) WORKERS="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --) shift; EXTRA+=("$@"); break ;;
    *) echo "未知参数: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$SUITE" in
  api|ui|all) ;;
  *) echo "suite 只能是 api、ui 或 all" >&2; exit 2 ;;
esac

if [ -d /workspace/qa ]; then
  QA_ROOT="${QA_ROOT:-/workspace/qa}"
else
  QA_ROOT="${QA_ROOT:-$REPO_DIR}"
fi

if [ "$DRY_RUN" != "1" ] && [ "${QA_SKIP_BOOTSTRAP:-0}" != "1" ]; then
  branch=$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
  if [ "$branch" = "HEAD" ]; then
    branch="main"
  fi
  url=$(git -C "$REPO_DIR" remote get-url origin 2>/dev/null || echo "https://github.com/bibuat1-stack/qa-agent-team")
  bash "$REPO_DIR/tools/bootstrap_bot_computer.sh" "$url" "$branch"
fi

if [ -f "$QA_ROOT/cloud.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$QA_ROOT/cloud.env"
  set +a
fi
export QA_CLOUD=1

PY_PLAN="${PYTHON:-python3}"
if [ -n "${VENV:-}" ] && [ -x "$VENV/bin/python" ]; then
  PY_TEST="$VENV/bin/python"
elif [ -x "$HOME/.venvs/qa/bin/python" ]; then
  PY_TEST="$HOME/.venvs/qa/bin/python"
elif [ -x "$REPO_DIR/.venv/bin/python" ]; then
  PY_TEST="$REPO_DIR/.venv/bin/python"
else
  PY_TEST="$PY_PLAN"
fi

explicit_target=0
looks_ui=0
if [ "${#EXTRA[@]}" -gt 0 ]; then
  for item in "${EXTRA[@]}"; do
    if [[ "$item" != -* ]]; then
      explicit_target=1
      if [[ "$item" == *"/ui/"* || "$item" == tests/ui* ]]; then
        looks_ui=1
      fi
    fi
  done
fi
# 点名了文件或节点时只跑这一次，不再把 api 和 ui 各跑一遍。
if [ "$explicit_target" = "1" ]; then
  if [ "$looks_ui" = "1" ]; then
    SUITES=(ui)
  else
    SUITES=(api)
  fi
elif [ "$SUITE" = "all" ]; then
  SUITES=(api ui)
else
  SUITES=("$SUITE")
fi

RUN_ID=$(date +%Y%m%d-%H%M%S)
if [ -e "$QA_ROOT/runs/$RUN_ID" ]; then
  RUN_ID="${RUN_ID}-$$"
fi
RUN_DIR="$QA_ROOT/runs/$RUN_ID"
mkdir -p "$RUN_DIR"
STARTED=$(date --iso-8601=seconds)
START_EPOCH=$(date +%s)

plan_for() {
  local suite="$1"
  local args=(plan --suite "$suite")
  if [ -n "$MARKERS" ]; then
    args+=(--markers "$MARKERS")
  fi
  if [ -n "$WORKERS" ]; then
    args+=(--workers "$WORKERS")
  fi
  if [ -n "${QA_CLOUD_MEM_MB:-}" ]; then
    args+=(--mem-mb "$QA_CLOUD_MEM_MB")
  fi
  if [ "${QA_CLOUD_FORCE_UI:-0}" = "1" ]; then
    args+=(--force-ui)
  fi
  "$PY_PLAN" -m tools.cloud_efficiency "${args[@]}"
}

declare -a SUITE_ROWS=()
WORST=0

remember_exit() {
  local code="$1"
  # 1 用例失败优先于 2 资源阻塞，2 优先于 5 没有收集到用例。
  if [ "$code" -eq 0 ] || [ "$WORST" -eq 1 ]; then
    return
  fi
  if [ "$code" -eq 1 ] || [ "$WORST" -eq 0 ]; then
    WORST=$code
    return
  fi
  if [ "$code" -eq 2 ] && [ "$WORST" -ne 2 ]; then
    WORST=2
  fi
}

for suite in "${SUITES[@]}"; do
  set +e
  plan_json=$(plan_for "$suite")
  plan_code=$?
  set -e
  if [ "$plan_code" -ne 0 ] && [ "$plan_code" -ne 2 ]; then
    echo "无法规划 $suite 的并发（退出码 $plan_code）" >&2
    exit "$plan_code"
  fi
  blocked=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("blocked",""))' <<<"$plan_json")
  note=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("note",""))' <<<"$plan_json")
  workers=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("workers",0))' <<<"$plan_json")
  markers=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("markers",""))' <<<"$plan_json")
  if [ -n "$note" ]; then
    echo "$note"
  fi
  if [ -n "$blocked" ]; then
    echo "$blocked"
    SUITE_ROWS+=("$(python3 -c 'import json,sys; print(json.dumps({"name":sys.argv[1],"exit_code":2,"blocked":sys.argv[2]}, ensure_ascii=False))' "$suite" "$blocked")")
    remember_exit 2
    continue
  fi

  allure_dir="$RUN_DIR/$suite/allure-results"
  html_file="$RUN_DIR/$suite/report.html"
  junit_file="$RUN_DIR/$suite/junit.xml"
  mkdir -p "$allure_dir"
  cmd=("$PY_TEST" "$REPO_DIR/run.py" --cloud --suite "$suite" --reruns "$RERUNS" --workers "$workers")
  if [ -n "$ENV_NAME" ]; then
    cmd+=(--env "$ENV_NAME")
  fi
  if [ -n "$markers" ]; then
    cmd+=(-m "$markers")
  fi
  cmd+=(--alluredir "$allure_dir" --html "$html_file" -- --junitxml="$junit_file")
  if [ "$suite" = "ui" ] && [ "${#EXTRA[@]}" -gt 0 ]; then
    has_output=0
    for item in "${EXTRA[@]}"; do
      if [ "$item" = "--output" ] || [[ "$item" == --output=* ]]; then
        has_output=1
      fi
    done
    if [ "$has_output" -eq 0 ]; then
      cmd+=(--output "$RUN_DIR/$suite/playwright")
    fi
  elif [ "$suite" = "ui" ]; then
    cmd+=(--output "$RUN_DIR/$suite/playwright")
  fi
  if [ "${#EXTRA[@]}" -gt 0 ]; then
    cmd+=("${EXTRA[@]}")
  fi

  echo "[run_cloud] ${cmd[*]}"
  if [ "$DRY_RUN" = "1" ]; then
    SUITE_ROWS+=("$(python3 -c 'import json,sys; print(json.dumps({"name":sys.argv[1],"exit_code":0,"junit":sys.argv[2],"note":"dry-run"}, ensure_ascii=False))' "$suite" "$junit_file")")
    continue
  fi

  set +e
  (cd "$REPO_DIR" && "${cmd[@]}")
  code=$?
  set -e
  remember_exit "$code"
  row_note=""
  if [ "$code" -eq 5 ]; then
    row_note="没有收集到用例"
  fi
  SUITE_ROWS+=("$(python3 -c 'import json,sys; print(json.dumps({"name":sys.argv[1],"exit_code":int(sys.argv[2]),"junit":sys.argv[3],"note":sys.argv[4]}, ensure_ascii=False))' "$suite" "$code" "$junit_file" "$row_note")")
done

if [ "$DRY_RUN" = "1" ]; then
  printf 'run_dir=%s\n' "$RUN_DIR"
  exit "$WORST"
fi

FINISHED=$(date --iso-8601=seconds)
WALL=$(( $(date +%s) - START_EPOCH ))
MEM=$("$PY_PLAN" -c 'from tools.cloud_efficiency import mem_available_mb; value=mem_available_mb(); print(-1 if value is None else value)')
ROWS_JSON=$(printf '%s\n' "${SUITE_ROWS[@]}" | python3 -c 'import json,sys; print(json.dumps([json.loads(line) for line in sys.stdin if line.strip()], ensure_ascii=False))')
RESOURCES_JSON=$(python3 -c 'import json,sys; print(json.dumps({"mem_available_mb": int(sys.argv[1])}, ensure_ascii=False))' "$MEM")

(
  cd "$REPO_DIR"
  "$PY_PLAN" -m tools.cloud_efficiency summarize \
    --run-dir "$RUN_DIR" \
    --environment "$ENV_NAME" \
    --started-at "$STARTED" \
    --finished-at "$FINISHED" \
    --wall-seconds "$WALL" \
    --resources-json "$RESOURCES_JSON" \
    --suites-json "$ROWS_JSON"
) || true
echo "-----"
cat "$RUN_DIR/summary.txt"
exit "$WORST"
