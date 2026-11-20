"""回收判定的本地检查。不登录，不访问生产。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verdicts import judge_recall, scrape_account_balances, scrape_game_wallet

ACCOUNT = """
Member567HXX0O
UID | 99999495
Available balance Freeze balance
₹0 ₹0 Detail
Safe
Daily interest
₹0.00
"""

WINGO = """
₹69.31
Wallet balance
Time remaining
00 : 13
2026112000500
Win Go 1Min
"""


def test_scrape_account_and_game_wallet():
    balances = scrape_account_balances(ACCOUNT)
    assert balances["available"] == 0
    assert balances["safe"] == 0
    assert scrape_game_wallet(WINGO) == 69.31


def test_recall_pass_when_main_wallet_increases_by_the_game_wallet():
    judged = judge_recall(
        {"available": 0, "safe": 0, "game_wallet": 69.31},
        {"available": 69.31, "safe": 0},
        200,
        200,
    )
    assert judged["verdict"] == "通过"


def test_recall_is_not_pass_when_game_wallet_stays_out_of_the_main_wallet():
    judged = judge_recall(
        {"available": 0, "safe": 90, "game_wallet": 908.28},
        {"available": 0, "safe": 90},
        200,
        200,
    )
    assert judged["verdict"] == "失败待核"


def test_http_200_without_balances_is_not_pass():
    judged = judge_recall(
        {"available": 0, "safe": None, "game_wallet": 10},
        {"available": 10, "safe": 0},
        200,
        200,
    )
    assert judged["verdict"] == "待确认"


def test_zero_game_wallet_can_pass_only_when_balances_are_recorded():
    judged = judge_recall(
        {"available": 0, "safe": 0, "game_wallet": 0},
        {"available": 0, "safe": 0},
        200,
        200,
    )
    assert judged["verdict"] == "通过"


def test_partial_increase_stays_unconfirmed():
    judged = judge_recall(
        {"available": 0, "safe": 0, "game_wallet": 100},
        {"available": 40, "safe": 0},
        200,
        200,
    )
    assert judged["verdict"] == "待确认"
