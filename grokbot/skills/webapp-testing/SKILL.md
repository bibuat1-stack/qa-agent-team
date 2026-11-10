---
name: webapp-testing
description: >-
  测本地或已启动的 Web 应用、写精简 Playwright Python 脚本、先侦察再动作时使用。适合配合 with_server
  启停前后端；远程业务站探路优先 playwright-cli / agent-browser / Playwright MCP。
---
# webapp-testing（机器人优化版）

来自 anthropics/skills。核心是：**先侦察再动作**，动态页必须等渲染后再找选择器；本地服务用 helper 管生命周期。

## 何时用

- 测本地前后端（dev server）
- 写短小 Playwright Python 脚本做验证
- 需要 `networkidle` 后再截图 / 挖按钮

远程业务站、登录走查、多会话测号：优先 [playwright-cli](sand-workflow:playwright-cli)、[agent-browser](sand-workflow:agent-browser) 或 Playwright MCP，并加载 [box-ui-speed](sand-workflow:box-ui-speed)。

## 决策树

```
静态 HTML？
  是 → 直接读文件找选择器 → 写 Playwright 脚本
动态页？
  服务未起 → python scripts/with_server.py --help（上游包内脚本）
  服务已起 → 打开 → wait networkidle → 截图/DOM → 再动作
```

上游 stub 在 `~/.agents/skills/webapp-testing/`。需要 helper 时先对该目录下 `scripts/with_server.py` 跑 `--help`，不要整文件塞进上下文。

## 最小脚本习惯

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:5173")
    page.wait_for_load_state("networkidle")
    # 再找 role/name/testId，少用脆弱 CSS
    browser.close()
```

## 机器人边界

- headless Chromium，不驱动桌面 Chrome 窗
- 凭证不进脚本明文提交到聊天/Notion/记忆
- 预期必须有依据；无范围不开测
- 跑通后把稳定路径升成项目 Playwright 回归脚本

来源：https://skills.sh/anthropics/skills/webapp-testing
