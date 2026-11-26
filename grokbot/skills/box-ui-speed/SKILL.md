---
name: box-ui-speed
description: >-
  在当前这台机器（Linux 云电脑或用户 Windows 电脑）上做浏览器或桌面 UI
  操作、走查、填表、点按钮之前使用。先按操作系统和本机已有环境选最合适且效率最高的方式，两套配置不要混用。约定优先接口与 Playwright
  脚本，网页探路三选一（Playwright MCP / playwright-cli / agent-browser），压缩 computerUse
  轮次。探路与写脚本由各项目自理，踩坑脱敏汇总交「自动化踩坑知识库」。自愈只换定位；断言按依据改：需求已写明或资金账务不得为跑绿改，需求没写清且非这两类可按实测改并标明依据。断言优先核对业务结果，不要只断言元素还在。
---
# Linux 机器人电脑 UI 提速

通用约定。不扩大项目授权，不跨项目借账号。

## 目标

少开桌面代理、少截图轮询、少猜坐标。能自动识别控件、自动跑通流程、自动写出可复用脚本。探路过程中 AI 必须实时纠偏定位，不要等整轮失败再回头。自愈只换定位策略。断言按依据改：需求已写明或资金账务不得为跑绿改；需求没写清且非资金账务、非需求已写明的点时，可按实测改并标明依据。断言优先核对业务结果（跳转、金额、状态、关键文案），不要只断言某个控件还在。

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


## 不抢浏览器，改脚本复用页面，并按本机选环境（2026-11-26）

默认追求效率最高，但不要套死一套工具。先认清当前是哪一台机器、什么系统，再看这台上已有什么，最后选最合适、效率最高的方式。Linux 云电脑和 Windows 本机的配置不一样，同一账号下的不同电脑也不共用一套环境。

先查：机器标识、系统与架构、shell（bash 或 PowerShell）、Node / npm、playwright-cli、Python Playwright、Chrome for Testing / headless shell、系统或平台桌面 Chrome（只记录，禁止驱动）、已打开的调试端口、已保存的登录态、当前网络。缺什么再补什么，已经能用的不要重装，也不要换一套去抢同一会话。探完后写清楚：选了哪套、为什么适合、系统、版本和路径、缺过什么、补了什么。不要只说「环境已就绪」却不写配置。各台版本不必强行对齐。登录态和调试端口不能跨机器用。换一台电脑就重新探。

1. 测试执行不要抢浏览器：禁止接或驱动平台桌面 Chrome；同一登录号同一时间只开一种探路工具，不要混开两套抢同一测号会话。
2. 改脚本不要每次重新开页面、重新登录。优先复用已打开的页面和已保存的登录态（只在当前这台机器上）。
3. 不盯画面、测打开速度、跑回归：优先无头 Chromium / Chrome for Testing。本机已有 CLI 就用 CLI，已有可用的脚本环境也可以用脚本。
4. 要盯着看：自己拉起有头 Chrome for Testing。能 `attach --cdp` 就接到已打开窗口，改一条再跑。只接自己拉起的窗口。Windows 上有头窗口会显示在用户屏幕上，但不要抢系统 Chrome。Linux 云电脑没有用户那种日常桌面，可用 `/workspace/qa/bin/open_direct_headed.py` 拉起后再 attach，启动常加 `--no-sandbox`。
5. 登录态用 playwright-cli 的 `state-save` / `state-load`，或本机已有的等价方式。
6. 若本机还没有合适工具：优先补 Node LTS + `@playwright/cli` + 对应系统的 Chrome for Testing（含 headless shell）。本机已有完整可用的 Python Playwright 且浏览器齐全时，可以先用现成的，不必强行再装一套来抢会话。Python 和 Node 可以并存。云电脑补齐先跑 `/workspace/qa/qa-ready.sh`，缺了才补，不跑 apt。Windows 用 PowerShell，不要套 bash 语法。
7. 网络要分环境：云电脑默认直连，不要一上来走 8791 代理或转发用户电脑流量。8791 不要套到 Windows 本机。用户电脑若本身需要 VPN 或系统代理，不要盲目关掉。只有打不开、被限制拦住，或用户当轮明确要求，才改走代理或转发。
8. 正式复测或回归下结论，仍须进入当前环境当轮现取证，不得拿以前的截图或旧数据当结论；这不妨碍改脚本时复用当轮已打开的页面和登录态文件。

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
2. **跑通**：按业务步骤用 ref 点击、填表、断言。每步动作后先验业务结果（URL/金额/状态/关键文案），控件状态作补充。可挂接口监听区分前后端。
3. **自愈**：同一步最多试 ① 项目库选择器 ② a11y role/name ③ SoM/可见文案。全失败则 fail-closed，记缺口，禁止连点乱试。自愈只换定位策略。断言按下面「断言按依据改」处理，不在当次失败里悄悄改期望当通过。
4. **落脚本（必做）**：流程首次完整跑通后，**当场**生成 Playwright 脚本（或补进现有 spec），写入本项目约定目录，步骤带知识点/用例编号注释。选择器写入本项目选择器库。写脚本时可先加载 `modern-web-guidance`。
5. **复用**：同一流程第二次起只跑脚本。脚本失败再探路修复，修完立刻更新脚本，不长期靠 MCP/CLI 手点。
6. **升级门槛**：连续成功 ≥2 次或用户明确要回归的路径，必须已有脚本，否则算未完成。

脚本最低要求：稳定定位（优先 getByRole/getByTestId）、关键断言有依据且优先核对业务结果（跳转、金额、状态、关键文案）、失败出 trace/截图路径、不用硬编码密钥。落盘时，需求已写明或资金账务不得把当次页面现状写进断言当做通过；需求没写清且非资金账务、非需求已写明的点时，按实测写断言必须标明「实测归纳」并写清依据。

## 实时自愈（探路必做）

1. **先读后点**：snapshot 再行动。
2. **命中即固化**：稳定点到后立刻写选择器与脚本片段。
3. **动作后验业务结果**：无变化就换策略，不空转。先验跳转、金额、状态、关键文案，不要只看某个控件还在。
4. **同类只学一次**：失效则更新库条目，不另起临时坐标。
5. **卡死判定**：同一目标连续失败 2 次或同态空转超限，立刻停并报告。
6. **断言按依据改**：自愈只换选择器或定位策略。写断言时优先核对业务结果（跳转、金额、状态、关键文案），不要只断言某个控件还在。需求已经写明或属于资金账务时，禁止为跑绿改写、放宽或删除断言。需求没写清，又不是资金账务或需求里已经写明的点时，可按页面实际改断言，必须标明「实测归纳」并写清依据，先改用例再重跑；不能在当次失败里悄悄改期望当通过。

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
