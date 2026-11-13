---
name: box-ui-speed
description: >-
  在 Linux 机器人电脑上做浏览器或桌面 UI 操作、走查、填表、点按钮之前使用。约定优先接口与 Playwright
  脚本，网页探路三选一（Playwright MCP / playwright-cli / agent-browser），压缩 computerUse
  轮次。探路与写脚本由各项目自理，踩坑脱敏汇总交「自动化踩坑知识库」。
---
# Linux 机器人电脑 UI 提速

通用约定。不扩大项目授权，不跨项目借账号。

## 目标

少开桌面代理、少截图轮询、少猜坐标。能自动识别控件、自动跑通流程、自动写出可复用脚本。探路过程中 AI 必须实时纠偏定位，不要等整轮失败再回头。

## 执行方交接（2026-11-09 纠正）

原「UI自动化协调」（id: 7f9ec681-8410-4441-9d55-95df8a2e4cad）已改名为「自动化踩坑知识库」。取消「探路交给 UI自动化协调」。该 id 不再做 UI 探路、不写/改 Playwright 脚本与选择器、不日常连跑。

UI 探路与写脚本：由各项目执行方自己或既有授权方式处理（Playwright MCP、[playwright-cli](sand-workflow:playwright-cli)、[agent-browser](sand-workflow:agent-browser)、box-ui-speed、必要时 Cursor 协助）。

自动化踩坑沉淀：遇到问题并解决后，把脱敏汇总交给「自动化踩坑知识库」（同 id）：项目名、现象、已尝试步骤、最终解法或仍未解原因、脱敏证据路径。禁止凭证。该库只沉淀可复用知识，不替执行方排障到底，也不接连跑。

框架级新设计仍先 Cursor 审核。T8T 新框架/试点按既有用户决定暂不推进。

## 选型（按优先级）

1. **有连接器或 API**：用 MCP/接口，不点页面。
2. **可重复回归**：只跑仓库 Playwright 脚本（或 Playwright MCP 复跑）。下次只跑脚本。
3. **网页探路与一次性走查**：三选一，**不要混开两套抢同一测号会话**。
   - **Playwright MCP**：accessibility snapshot + ref（连接器可用时首选）
   - **[playwright-cli](sand-workflow:playwright-cli)**：Shell 驱动、`-s=` 会话隔离、snapshot/录制/requests/console/trace（官方 CLI）
   - **[agent-browser](sand-workflow:agent-browser)**：独立 Chromium、`snapshot -i` / `@eN`、`--session`
4. **本地 Web 应用/dev server**：可加载 [webapp-testing](sand-workflow:webapp-testing)（先侦察再动作、`networkidle`、with_server）。远程业务站仍走第 3 条。
5. **探路跑通后固化**：当场写成 Playwright 脚本落盘（角色/可访问名定位，开 trace）。第二次起回到第 2 条。写脚本时可加载 `modern-web-guidance`。
6. **一次性探路且网页工具够不到**（原生桌面、canvas、必须看桌面浏览器窗）：才用 computerUse。
7. **禁止**：用 Shell 的 xdotool、CDP、Playwright 去驱动机器人电脑**自带桌面浏览器窗口**（平台边界）。playwright-cli / agent-browser / 仓库 Playwright 跑的是独立浏览器或目标站点，不等于操控桌面 Chrome。

## playwright-cli 要点

- 务必 `-s=<项目短名>`，默认会话会互相踩
- 核心：`open` → `snapshot` → `click/fill eN` → `requests`/`console` → `close`
- 详情见 [playwright-cli](sand-workflow:playwright-cli)

## agent-browser 要点

- 首次用前：`agent-browser skills get core`，任务用独立 `--session`
- 详情与安全边界见 [agent-browser](sand-workflow:agent-browser)
- 登录仍走 sign-in / vault，凭证不进聊天

## Modern Web Guidance（探路写脚本）

1. 用户已装 Modern Web Guidance（插件 6398877）。**仅用于探路与落 Playwright 脚本时**加载 `modern-web-guidance`，补现代 Web、无障碍与稳定定位写法。
2. 不替代 Playwright MCP/脚本执行，不替代接口监听与验收门禁，不接入正式连跑主循环。
3. 优先用 role/label/testId 与语义化断言。少猜坐标，少脆弱纯 CSS。
4. `chrome-extensions` 技能仅在扩展相关任务时用，日常 Web 业务探路默认只加载 `modern-web-guidance`。

## 自动识别 → 自动跑 → 自动写脚本

把每次探路当成「录制并固化」：

1. **识别**：用 Playwright MCP `browser_snapshot` / playwright-cli `snapshot` / agent-browser `snapshot -i` / a11y 树拿到控件 ref、role、name。禁止一上来猜坐标。
2. **跑通**：按业务步骤用 ref 点击、填表、断言。每步动作后验状态（URL/文案/控件）。可挂接口监听区分前后端。
3. **自愈**：同一步最多试 ① 项目库选择器 ② a11y role/name ③ SoM/可见文案。全失败则 fail-closed，记缺口，禁止连点乱试。
4. **落脚本（必做）**：流程首次完整跑通后，**当场**生成 Playwright 脚本（或补进现有 spec），写入本项目约定目录，步骤带知识点/用例编号注释。选择器写入本项目选择器库。写脚本时可先加载 `modern-web-guidance`。
5. **复用**：同一流程第二次起只跑脚本。脚本失败再探路修复，修完立刻更新脚本，不长期靠 MCP/CLI 手点。
6. **升级门槛**：连续成功 ≥2 次或用户明确要回归的路径，必须已有脚本，否则算未完成。

脚本最低要求：稳定定位（优先 getByRole/getByTestId）、关键断言有依据、失败出 trace/截图路径、不用硬编码密钥。

## 实时自愈（探路必做）

1. **先读后点**：snapshot 再行动。
2. **命中即固化**：稳定点到后立刻写选择器与脚本片段。
3. **动作后验状态**：无变化就换策略，不空转。
4. **同类只学一次**：失效则更新库条目，不另起临时坐标。
5. **卡死判定**：同一目标连续失败 2 次或同态空转超限，立刻停并报告。

## 失败读报告（本项目产物）

1. 先读本项目约定的 HTML report / trace / 截图 / 接口摘要路径，不要去微软 Playwright 上游 CI DuckDB。
2. 结论只写本跑次真实结果。区分前端（DOM/文案）与接口（status/body）。
3. 可加载 [playwright-report-triage](sand-workflow:playwright-report-triage)（若已装）。

## computerUse 派工提速

1. **一次一事**：每个任务一个可验收结果。
2. **给深链**：已知 URL 写完整地址。
3. **成功标准写死**：标题、可访问名、URL 片段、必须/禁止文案。
4. **同流复用**：MessageSubagent / resume，避免冷启动。
5. **先读后点**：a11y 优先，像素仅一次兜底。
6. **少汇报**：结论、策略、是否已落脚本、证据路径。
7. **批量数据**：Shell 生成文件后导入。
8. **登录**：按 sign-in / in-chat-forms。

## 主控侧习惯

1. 超过两轮桌面活必须派 computerUse，网页优先 Playwright MCP、playwright-cli 或 agent-browser。
2. 不轮询 CheckSubagent。
3. 同时只跑一个 computerUse。
4. 站点有 `site-playbooks-*` 时先加载。
5. 电脑异常先 `box-doctor`，再考虑 [Update Bot's Computer](grokbot://app/v1/settings?id=update-computer)。
