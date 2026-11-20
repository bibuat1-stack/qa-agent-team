"""生产前台安全路径。不下注，不充提，不领取，不注册。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import expect, sync_playwright

from verdicts import judge_recall, scrape_account_balances, scrape_game_wallet

VIEWPORT = {"width": 430, "height": 900}
FORBIDDEN_CLICK = re.compile(
    r"receive|participate|spin|install|detail|deposit now|get started|claim|random|\bbig\b|\bsmall\b",
    re.I,
)
SKIP_PAGE = re.compile(
    r"does not support your|not available in your (region|country)|under maintenance|系统维护|IP不支持|当前地区",
    re.I,
)
PLAY_SCREEN = re.compile(
    r"Time remaining|How to play|Win Go\s*1Min|Win Go\s*30S|\d{10,}",
    re.I,
)


def run_flow(site: dict, phone: str, password: str, step: str, evidence: Path, headed: bool) -> dict:
    evidence.mkdir(parents=True, exist_ok=True)
    result = {
        "site": site["key"],
        "name": site["name"],
        "entry": site["entry"],
        "phone": phone,
        "step": step,
        "checks": [],
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=not headed,
            args=["--no-proxy-server", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport=VIEWPORT,
            locale="en-US",
            proxy={"server": "direct://"},
        )
        page = context.new_page()
        try:
            skip = _open_entry(page, site["entry"], evidence, result)
            if skip:
                return result
            _login(page, phone, password, evidence, result)
            if not _login_ok(result):
                return result
            if step in ("nav", "all"):
                _nav(page, evidence, result)
            if step in ("wingo", "recall", "switch", "all"):
                _enter_wingo(page, evidence, result)
            if step in ("recall", "switch", "all"):
                _recall(page, evidence, result)
            if step in ("switch", "all"):
                _switch_vendor(page, evidence, result)
        except PlaywrightTimeout as exc:
            result["checks"].append(
                {
                    "id": "timeout",
                    "verdict": "阻塞",
                    "source": "脚本等待超时",
                    "detail": str(exc).split("\n", 1)[0][:300],
                }
            )
        finally:
            _write_json(evidence / "result.json", result)
            context.close()
            browser.close()
    return result


def _open_entry(page, entry: str, evidence: Path, result: dict) -> bool:
    try:
        page.goto(entry, wait_until="domcontentloaded", timeout=30000)
    except PlaywrightTimeout:
        result["checks"].append(
            {
                "id": "open",
                "verdict": "跳过",
                "source": "派单安全路径",
                "detail": "入口打开超时。无法访问记跳过，不算通过或缺陷。",
            }
        )
        return True
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    page.context.clear_cookies()
    page.goto(entry, wait_until="domcontentloaded", timeout=30000)
    text = page.inner_text("body")
    _shot(page, evidence, "01-entry.png")
    if SKIP_PAGE.search(text):
        result["checks"].append(
            {
                "id": "open",
                "verdict": "跳过",
                "source": "派单安全路径",
                "detail": "页面提示地区、IP 或维护。记跳过，不算通过或缺陷。",
            }
        )
        return True
    return False


def _login(page, phone: str, password: str, evidence: Path, result: dict) -> None:
    _close_popups(page)
    if page.locator("input[type=password]").count() == 0:
        header = page.get_by_text("Log in", exact=True)
        if header.count() == 0:
            result["checks"].append(
                {
                    "id": "login",
                    "verdict": "未验证",
                    "source": "派单安全路径",
                    "detail": "没有找到登录入口，也没有密码框。",
                }
            )
            return
        header.first.click()
        expect(page.locator("input[type=password]").first).to_be_visible(timeout=15000)
    phone_box = page.locator(
        "input[type=tel], input[type=number], input[type=text]"
    ).first
    phone_box.fill(phone)
    page.locator("input[type=password]").first.fill(password)
    submit = page.locator(".loginBtn")
    if submit.count() == 0:
        result["checks"].append(
            {
                "id": "login",
                "verdict": "未验证",
                "source": "派单安全路径",
                "detail": "没有找到 .loginBtn。页头 Log in 文字不会发出登录请求，脚本没有改点它。",
            }
        )
        return
    captured = {}
    try:
        with page.expect_response(_is_player_login, timeout=20000) as pending:
            submit.first.click()
        response = pending.value
        captured = _response_brief(response)
    except PlaywrightTimeout:
        result["checks"].append(
            {
                "id": "login",
                "verdict": "未验证",
                "source": "派单安全路径",
                "detail": "点击 .loginBtn 后没有发出 POST /auth/playerLogin。",
            }
        )
        return
    try:
        expect(page.locator("input[type=password]")).not_to_be_visible(timeout=15000)
    except AssertionError:
        result["checks"].append(
            {
                "id": "login",
                "verdict": "失败",
                "source": "派单安全路径",
                "detail": "登录请求已发出，密码框仍在。接口摘要：" + json.dumps(captured, ensure_ascii=False),
            }
        )
        return
    _click_tab(page, "Account")
    body = page.inner_text("body")
    _shot(page, evidence, "02-account.png")
    member = re.search(r"Member[A-Za-z0-9]+", body)
    if member and "UID" in body and "Available balance" in body:
        result["balances_before"] = scrape_account_balances(body)
        result["checks"].append(
            {
                "id": "login",
                "verdict": "待确认",
                "source": "派单安全路径",
                "confirmed_case_id": None,
                "detail": (
                    f"信号符合：已离开登录页，看到会员 {member.group(0)} 和 UID。"
                    "没有正式用例编号，不能写成验收通过。"
                ),
                "response": captured,
                "balances": result["balances_before"],
            }
        )
        return
    result["checks"].append(
        {
            "id": "login",
            "verdict": "失败",
            "source": "派单安全路径",
            "detail": "离开了登录页，但账号页没有同时出现会员名、UID 和可用余额。",
            "response": captured,
        }
    )


def _nav(page, evidence: Path, result: dict) -> None:
    expectations = {
        "Home": ("Lottery", "Hot games", "Popular"),
        "Promotion": ("Activity",),
        "Agent": ("Agency", "Club", "commission", "rebate"),
        "Account": ("Available balance", "UID"),
    }
    for name, phrases in expectations.items():
        try:
            _click_tab(page, name)
        except PlaywrightTimeout:
            result["checks"].append(
                {
                    "id": f"nav-{name.lower()}",
                    "verdict": "未验证",
                    "source": "派单安全路径",
                    "detail": f"没有点到高亮为 {name} 的底栏。不把点偏记成该页缺失。",
                }
            )
            continue
        body = page.inner_text("body")
        _shot(page, evidence, f"03-nav-{name.lower()}.png")
        active = page.locator(".tabbar-item-active").inner_text(timeout=5000)
        if name not in active:
            result["checks"].append(
                {
                    "id": f"nav-{name.lower()}",
                    "verdict": "未验证",
                    "source": "派单安全路径",
                    "detail": f"当前高亮是 {active.strip()[:40]}，不是 {name}。",
                }
            )
            continue
        if any(phrase.lower() in body.lower() for phrase in phrases):
            result["checks"].append(
                {
                    "id": f"nav-{name.lower()}",
                    "verdict": "待确认",
                    "source": "派单安全路径",
                    "confirmed_case_id": None,
                    "detail": (
                        f"信号符合：高亮是 {name}，正文命中 {phrases}。"
                        "这些英文词没有正式用例编号，不能写成验收通过。"
                    ),
                }
            )
        else:
            result["checks"].append(
                {
                    "id": f"nav-{name.lower()}",
                    "verdict": "待确认",
                    "source": "派单安全路径",
                    "detail": f"高亮是 {name}，正文没有命中 {phrases}。没有正式编号，不写成失败。",
                }
            )


def _enter_wingo(page, evidence: Path, result: dict) -> None:
    _click_tab(page, "Home")
    _close_popups(page)
    point = _card_point(page, "Win Go")
    if not point:
        result["checks"].append(
            {
                "id": "wingo",
                "verdict": "未验证",
                "source": "MSK-3",
                "detail": "没有点到 Win Go 卡片。没有改去点 GO、数字或颜色。",
            }
        )
        return
    captured = {}
    try:
        with page.expect_response(_is_enter_game, timeout=20000) as pending:
            page.mouse.click(point["x"], point["y"])
        captured = _response_brief(pending.value)
    except PlaywrightTimeout:
        captured = {"note": "未在 20 秒内看到 POST /app/game/enterGame"}
    body = page.inner_text("body")
    _shot(page, evidence, "04-wingo.png")
    play_visible = PLAY_SCREEN.search(body) is not None
    result["game_wallet_before"] = scrape_game_wallet(body)
    result["saw_wingo_page"] = True
    if play_visible:
        result["checks"].append(
            {
                "id": "wingo",
                "verdict": "通过",
                "source": "MSK-3",
                "confirmed_case_id": "MSK-3",
                "detail": "玩法画面已出现（倒计时、玩法说明、期号或 Win Go 档位）。未下注。",
                "response": captured,
                "game_wallet": result["game_wallet_before"],
            }
        )
        return
    result["checks"].append(
        {
            "id": "wingo",
            "verdict": "未验证",
            "source": "MSK-3",
            "confirmed_case_id": "MSK-3",
            "detail": "没有看到玩法画面。只靠地址变化或 HTTP 200 不算通过。",
            "response": captured,
        }
    )


def _recall(page, evidence: Path, result: dict) -> None:
    before_balances = dict(result.get("balances_before") or {})
    if before_balances.get("available") is None or before_balances.get("safe") is None:
        _click_tab(page, "Account")
        before_balances = scrape_account_balances(page.inner_text("body"))
        result["balances_before"] = before_balances
    if result.get("game_wallet_before") is None and not result.get("saw_wingo_page"):
        result["checks"].append(
            {
                "id": "recall",
                "verdict": "未测",
                "source": "用户回收规则",
                "detail": "还没有读到游戏钱包。单独跑回收前需要先进入 Win Go。",
            }
        )
        return
    brief = {"found": False, "http_status": None, "outer_code": None}
    try:
        with page.expect_response(_is_withdraw, timeout=20000) as pending:
            raw = page.evaluate(_WITHDRAW_JS)
        response = pending.value
        brief = _response_brief(response)
        if isinstance(raw, dict):
            brief["found"] = bool(raw.get("found"))
            brief["module_found"] = raw.get("found")
            if raw.get("reason"):
                brief["reason"] = raw.get("reason")
    except PlaywrightTimeout:
        brief = {"found": False, "http_status": None, "outer_code": None, "reason": "no-withdrawAllVendor-response"}
    _click_tab(page, "Account")
    account_after = page.inner_text("body")
    _shot(page, evidence, "05-after-recall.png")
    after_balances = scrape_account_balances(account_after)
    before = {
        "available": before_balances.get("available"),
        "safe": before_balances.get("safe"),
        "game_wallet": result.get("game_wallet_before"),
    }
    after = {
        "available": after_balances.get("available"),
        "safe": after_balances.get("safe"),
    }
    judged = judge_recall(
        before,
        after,
        brief.get("http_status"),
        brief.get("outer_code"),
    )
    result["checks"].append(
        {
            "id": "recall",
            "verdict": judged["verdict"],
            "source": "用户回收规则",
            "detail": judged["reason"],
            "before": before,
            "after": after,
            "response": {
                "http_status": brief.get("http_status"),
                "outer_code": brief.get("outer_code"),
                "msg": brief.get("msg"),
                "found": brief.get("found"),
            },
        }
    )
    result["recall_verdict"] = judged["verdict"]


def _switch_vendor(page, evidence: Path, result: dict) -> None:
    recall = result.get("recall_verdict")
    if recall != "通过":
        result["checks"].append(
            {
                "id": "switch",
                "verdict": "未测",
                "source": "派单安全路径",
                "detail": "回收没有通过，停止跨厂商切换。",
            }
        )
        return
    _click_tab(page, "Home")
    closed = _close_popups(page)
    if not closed:
        result["checks"].append(
            {
                "id": "switch",
                "verdict": "未验证",
                "source": "派单安全路径",
                "detail": "二次弹窗没有关掉。不把弹窗挡住写成产品进不去。",
            }
        )
        _shot(page, evidence, "06-switch-blocked.png")
        return
    point = _card_point(page, "Aviator", square_only=True)
    if not point:
        result["checks"].append(
            {
                "id": "switch",
                "verdict": "未验证",
                "source": "派单安全路径",
                "detail": "没有点到接近正方形的 Aviator 卡片。没有改点赔率或标题文字。",
            }
        )
        return
    try:
        with page.expect_response(_is_enter_game, timeout=15000) as pending:
            page.mouse.click(point["x"], point["y"])
        brief = _response_brief(pending.value)
    except PlaywrightTimeout:
        result["checks"].append(
            {
                "id": "switch",
                "verdict": "阻塞",
                "source": "派单安全路径",
                "detail": "点了正方形卡片，但没有发出 enterGame。记阻塞，不写成产品进不去。",
            }
        )
        _shot(page, evidence, "06-switch.png")
        return
    _shot(page, evidence, "06-switch.png")
    result["checks"].append(
        {
            "id": "switch",
            "verdict": "待确认",
            "source": "派单安全路径",
            "detail": "已发出 enterGame。换厂商后的玩法画面没有已确认编号，不能只靠这个请求写成通过。",
            "response": brief,
        }
    )


def _click_tab(page, name: str) -> None:
    tab = page.locator(".tabbar-item").filter(has_text=re.compile(rf"\b{name}\b"))
    expect(tab.first).to_be_visible(timeout=10000)
    tab.first.click()
    expect(page.locator(".tabbar-item-active")).to_contain_text(name, timeout=10000)


def _close_popups(page) -> bool:
    forbid = FORBIDDEN_CLICK
    for _ in range(5):
        popup = page.locator(".u-popup:visible, .globalNotice:visible, .downloadDialog-android:visible")
        blockers = []
        for index in range(popup.count()):
            item = popup.nth(index)
            if item.locator("input[type=password]").count() == 0:
                blockers.append(item)
        if not blockers:
            return True
        popup = blockers[0]
        closer = popup.locator(
            "[class*='close'], [aria-label='close'], [aria-label='Close']"
        )
        clicked = False
        for index in range(closer.count()):
            item = closer.nth(index)
            text = item.inner_text(timeout=1000) if item.count() else ""
            if forbid.search(text or ""):
                continue
            item.click(timeout=2000)
            clicked = True
            break
        if not clicked:
            return False
        try:
            popup.first.wait_for(state="hidden", timeout=2000)
        except PlaywrightTimeout:
            continue
    return page.locator(".u-popup:visible, .globalNotice:visible").count() == 0


def _card_point(page, name: str, square_only: bool = False):
    point = page.evaluate(
        """({ name, squareOnly, forbid }) => {
          const wanted = name.toLowerCase();
          const nodes = [...document.querySelectorAll('uni-view, view, div, span, p')];
          const label = nodes.find((el) => {
            const text = (el.innerText || '').trim().toLowerCase();
            return text === wanted && el.getBoundingClientRect().width > 0;
          });
          if (!label) return null;
          let card = label.parentElement || label;
          let node = label;
          for (let step = 0; step < 3 && node.parentElement; step += 1) {
            const parent = node.parentElement;
            const rect = parent.getBoundingClientRect();
            const lines = (parent.innerText || '').trim().split(/\n/).filter(Boolean);
            if (rect.width > 240 || rect.height > 280 || lines.length > 6) break;
            card = parent;
            node = parent;
          }
          const labelRect = label.getBoundingClientRect();
          const boxes = [...card.querySelectorAll('img, uni-image, div, uni-view')];
          const squares = [];
          for (const el of boxes) {
            const rect = el.getBoundingClientRect();
            if (rect.width < 56 || rect.height < 56) continue;
            const ratio = rect.width / rect.height;
            const cls = String(el.className || '');
            if (/odd/i.test(cls)) continue;
            if (ratio < 0.75 || ratio > 1.35) continue;
            const distance = Math.abs((rect.x + rect.width / 2) - (labelRect.x + labelRect.width / 2));
            squares.push({ rect, distance });
          }
          squares.sort((a, b) => a.distance - b.distance || (a.rect.width * a.rect.height) - (b.rect.width * b.rect.height));
          const rect = squares[0] && squares[0].rect;
          if (!rect && squareOnly) return null;
          const target = rect || label.getBoundingClientRect();
          const x = target.x + target.width / 2;
          const y = target.y + Math.min(target.height / 2, target.height - 8);
          const top = document.elementFromPoint(x, y);
          if (!top || !card.contains(top)) return null;
          const topText = (top.innerText || '').trim();
          if (forbid && new RegExp(forbid, 'i').test(topText)) return null;
          return { x, y };
        }""",
        {"name": name, "squareOnly": square_only, "forbid": FORBIDDEN_CLICK.pattern},
    )
    return point


def _is_player_login(response) -> bool:
    return response.request.method == "POST" and "/auth/playerLogin" in response.url


def _is_enter_game(response) -> bool:
    return response.request.method == "POST" and "/app/game/enterGame" in response.url


def _is_withdraw(response) -> bool:
    return response.request.method == "POST" and "/app/vendor/withdrawAllVendor" in response.url


def _response_brief(response) -> dict:
    brief = {"http_status": response.status, "path": _path_only(response.url)}
    try:
        body = response.json()
    except Exception:
        return brief
    if isinstance(body, dict):
        brief["outer_code"] = body.get("code")
        message = body.get("msg") or body.get("message")
        if isinstance(message, str) and "token" not in message.lower():
            brief["msg"] = message[:120]
    return brief


def _path_only(url: str) -> str:
    match = re.search(r"https?://[^/]+(/[^?]*)", url)
    return match.group(1) if match else ""


def _shot(page, evidence: Path, name: str) -> None:
    page.screenshot(path=str(evidence / name))


def _write_json(path: Path, payload: dict) -> None:
    safe = dict(payload)
    safe.pop("account_text_before", None)
    safe.pop("wingo_body", None)
    safe.pop("saw_wingo_page", None)
    path.write_text(json.dumps(safe, ensure_ascii=False, indent=2), encoding="utf-8")


def _login_ok(result: dict) -> bool:
    login = next((item for item in result["checks"] if item.get("id") == "login"), None)
    if not login:
        return False
    return login.get("verdict") == "待确认" and str(login.get("detail", "")).startswith("信号符合")


_WITHDRAW_JS = r"""
async () => {
  const jsonp = window.webpackJsonp;
  if (!jsonp || typeof jsonp.push !== 'function') {
    return { found: false, reason: 'no-webpackJsonp' };
  }
  let requireRef = null;
  jsonp.push([[String(Date.now())], {}, (require) => { requireRef = require; }]);
  const cache = requireRef && requireRef.c;
  if (!cache) return { found: false, reason: 'no-module-cache' };
  for (const id of Object.keys(cache)) {
    const exports = cache[id] && cache[id].exports;
    const fn = exports && (exports.withdrawAllVendor || (exports.default && exports.default.withdrawAllVendor));
    if (typeof fn !== 'function') continue;
    try {
      await fn({});
    } catch (error) {
      return { found: true, reason: 'call-threw' };
    }
    return { found: true, reason: 'called' };
  }
  return { found: false, reason: 'withdrawAllVendor-not-exported' };
}
"""
