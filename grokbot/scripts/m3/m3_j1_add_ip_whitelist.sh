#!/usr/bin/env bash
# Add an IP to j1 admin IP whitelist. Token is read from the local secrets file, never printed.
set -euo pipefail
ENV_FILE="${M3_J1_WHITELIST_ENV:-/workspace/qa/secrets/m3-j1-ip-whitelist.env}"
IP="${1:-}"
REMARK="${2:-qa}"
if [[ -z "$IP" ]]; then
  echo "usage: $0 <ip> [remark]" >&2
  exit 2
fi
if [[ ! "$IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(/[0-9]+)?$ ]]; then
  echo "invalid ip: $IP" >&2
  exit 2
fi
if [[ ! -f "$ENV_FILE" ]]; then
  echo "missing secrets file" >&2
  exit 1
fi
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
if [[ -z "${BEARER_TOKEN:-}" || -z "${WHITELIST_URL:-}" ]]; then
  echo "secrets file incomplete" >&2
  exit 1
fi
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
code="$(curl -sS -o "$TMP" -w "%{http_code}" --url "$WHITELIST_URL" \
  -H 'Accept: application/json, text/plain, */*' \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H 'Content-Type: application/json;charset=UTF-8' \
  -H "Origin: ${WHITELIST_ORIGIN:-https://j1-m3-web.newopsname.com}" \
  -H "Referer: ${WHITELIST_ORIGIN:-https://j1-m3-web.newopsname.com}/" \
  -H "tenant-id: ${TENANT_ID:-1}" \
  --data-raw "{\"ipRule\":\"$IP\",\"remark\":\"$REMARK\",\"status\":1}")"
python3 - "$code" "$TMP" "$IP" << 'PY'
import json,sys,re,pathlib
code, path, ip = sys.argv[1], sys.argv[2], sys.argv[3]
raw = pathlib.Path(path).read_text(errors="replace")
def scrub(o):
    if isinstance(o, dict):
        return {k: ("[redacted]" if re.search(r"token|auth|password|secret|otp|bearer", k, re.I) else scrub(v)) for k,v in o.items()}
    if isinstance(o, list):
        return [scrub(x) for x in o]
    if isinstance(o, str) and re.fullmatch(r"[0-9a-fA-F]{32}", o):
        return "[redacted]"
    return o
print(f"ip={ip}")
print(f"http_code={code}")
try:
    print(json.dumps(scrub(json.loads(raw)), ensure_ascii=False))
except Exception:
    print(re.sub(r"Bearer\s+[A-Za-z0-9._\-]+", "Bearer [redacted]", raw)[:2000])
sys.exit(0 if code == "200" else 1)
PY