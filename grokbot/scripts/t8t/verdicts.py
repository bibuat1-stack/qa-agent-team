"""回收判定。不访问网络，方便本地检查。

依据是用户已确认的规则：进游戏时游戏钱包和账号钱包分开是正常的。
游戏钱包大于 0 时，回收后主钱包可用余额没有增加，不能写成通过。
只看到 HTTP 200 或外层 code 200，也不能写成通过。
"""

from __future__ import annotations

import re

PASS = "通过"
FAIL = "失败"
FAIL_REVIEW = "失败待核"
UNCONFIRMED = "待确认"

MONEY = r"(₹\s*[0-9][0-9,]*(?:\.[0-9]+)?)"


def parse_amount(raw: str | None) -> float | None:
    if not raw:
        return None
    match = re.search(r"([0-9][0-9,]*(?:\.[0-9]+)?)", raw.replace("₹", ""))
    if not match:
        return None
    return float(match.group(1).replace(",", ""))


def scrape_account_balances(text: str) -> dict:
    """从账号页正文读可用余额和保险箱。读不到则为 None。"""
    available = _first_amount_after(text, r"Available balance")
    safe = _first_amount_after(text, r"\bSafe\b")
    return {"available": available, "safe": safe}


def scrape_game_wallet(text: str) -> float | None:
    """游戏页金额在 Wallet balance 这几个字上面。"""
    match = re.search(MONEY + r"[\s\S]{0,40}?Wallet balance", text, re.I)
    if not match:
        return None
    return parse_amount(match.group(1))


def judge_recall(before: dict, after: dict, http_status: int | None, outer_code) -> dict:
    """返回 verdict 和 reason。balances 缺一项就不能通过。"""
    available_before = before.get("available")
    safe_before = before.get("safe")
    game_before = before.get("game_wallet")
    available_after = after.get("available")
    safe_after = after.get("safe")
    recorded = None not in (
        available_before,
        safe_before,
        game_before,
        available_after,
        safe_after,
    )
    if not recorded:
        return {
            "verdict": UNCONFIRMED,
            "reason": "账号可用余额、保险箱或游戏钱包没有读全，不能凭接口状态写成通过。",
        }
    if not _is_200(http_status) or not _is_200(outer_code):
        return {
            "verdict": FAIL,
            "reason": "回收接口没有同时返回 HTTP 200 和外层 code 200。",
        }
    increased = available_after > available_before + 0.009
    if game_before > 0 and not increased:
        return {
            "verdict": FAIL_REVIEW,
            "reason": (
                "进入前游戏钱包大于 0，回收后主钱包可用余额没有增加。"
                "进游戏时两钱包分开是正常的，不能用来解释回收后主钱包仍不增加。"
            ),
        }
    if game_before > 0 and increased and available_after + 0.05 < available_before + game_before:
        return {
            "verdict": UNCONFIRMED,
            "reason": "主钱包有增加，但增加额小于进入前的游戏钱包。没有已确认规则要求必须全额回到主钱包。",
        }
    if game_before <= 0 and available_after + 0.009 < available_before:
        return {
            "verdict": UNCONFIRMED,
            "reason": "进入前游戏钱包为 0，回收后主钱包可用余额却变少。",
        }
    return {
        "verdict": PASS,
        "reason": "三处余额都已记录。游戏钱包为 0，或主钱包可用余额已增加，且增加额覆盖了进入前的游戏钱包。",
    }


def _is_200(value) -> bool:
    try:
        return int(value) == 200
    except (TypeError, ValueError):
        return False


def _first_amount_after(text: str, label: str) -> float | None:
    match = re.search(label + r"[\s\S]{0,180}?" + MONEY, text, re.I)
    if not match:
        return None
    return parse_amount(match.group(1))
