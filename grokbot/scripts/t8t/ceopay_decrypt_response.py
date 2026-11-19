#!/usr/bin/env python3
"""CEOpay 加密返回解密。只把解密结果打到标准输出，不保存 cookie。"""
from __future__ import annotations

import json
import sys
import http.cookiejar
import urllib.error
import urllib.request

DECRYPT_URL = "https://www.i2lok5t.com/api/decrypt-response"
HOME_URL = "https://www.i2lok5t.com/"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/157.0.0.0 Safari/537.36"
)


def parse_input(raw: str) -> dict:
    text = raw.strip()
    if not text:
        raise ValueError("空输入")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError("不是合法 JSON") from e
    if isinstance(obj, dict) and "data" in obj:
        return obj
    raise ValueError("缺少 data 字段")


def opener():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(HOME_URL, headers={"User-Agent": UA, "Accept": "text/html"})
    with op.open(req, timeout=15) as r:
        r.read(256)
    return op


def decrypt(outer: dict) -> dict:
    body = json.dumps({"data": json.dumps(outer, separators=(",", ":"))}, ensure_ascii=False).encode()
    req = urllib.request.Request(
        DECRYPT_URL,
        data=body,
        headers={
            "User-Agent": UA,
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": "https://www.i2lok5t.com",
            "Referer": "https://www.i2lok5t.com/",
        },
        method="POST",
    )
    op = opener()
    try:
        with op.open(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", "replace")
        try:
            return json.loads(err_body)
        except json.JSONDecodeError:
            return {"ok": False, "error": f"HTTP {e.code}"}


def render(result: dict) -> int:
    if not result.get("ok"):
        print("解不出来。")
        return 1
    dec = result.get("decrypted")
    mode = result.get("mode") or "response"
    print("解密结果")
    print(f"模式: {mode}")
    print()
    if isinstance(dec, (dict, list)):
        print(json.dumps(dec, ensure_ascii=False, indent=2))
    else:
        print(dec if dec is not None else json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] not in ("-h", "--help"):
        raw = " ".join(argv)
    else:
        raw = sys.stdin.read()
    if not raw.strip() or (argv and argv[0] in ("-h", "--help")):
        print("用法: ceopay_decrypt_response.py '<加密返回 JSON>'", file=sys.stderr)
        print("或: 把加密返回 JSON 从标准输入传入", file=sys.stderr)
        return 2
    try:
        outer = parse_input(raw)
    except ValueError:
        print("解不出来。")
        return 1
    try:
        result = decrypt(outer)
    except Exception:
        print("解不出来。")
        return 1
    return render(result)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
