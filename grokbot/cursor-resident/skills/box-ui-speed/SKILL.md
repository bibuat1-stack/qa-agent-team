---
name: box-ui-speed
description: >-
  在 Linux 机器人电脑上做浏览器或桌面 UI 操作、走查、填表、点按钮之前使用。独管探路：网页默认 playwright-cli（开批
  tracing-start，收批 tracing-stop），Playwright MCP 只用于不需要路径留痕的快速查看，agent-browser
  为备用。命令细节见 playwright-cli。不用于必须改派桌面子代理。
---
# Linux 机器人电脑 UI 提速

通用约定。不扩大项目授权，不跨项目借账号。

## 目标

少开桌面代理、少截图轮询、少猜坐标。能自动识别控件、自动跑通流程、自动写出可复用脚本。探路过程中 AI 必须实时纠偏定位，不要等整轮失败再回头。

## 默认直连（2026-11-10 确认）

页面工作默认走云电脑直连，不把流量送进 `127.0.0.1:8791`，也不为此设置 `HTTP_PROXY`、`HTTPS_PROXY`、`--proxy` 或 `--proxy-server`。平台自带桌面浏览器会被强制走该代理，且现有边界内改不了它的启动参数，所以能不经过它就不经过。

开工前先定本次走哪条，写入本次 handoff。走最后一行要写明理由。

| 场景 | 用什么 | 经过 8791 |
| --- | --- | --- |
| 接口断言、造数、查状态 | 接口或连接器 | 否 |
| 可重复的 UI 回归 | 仓库 Playwright 无头，加载登录态文件 | 否 |
| 探路 | 默认 playwright-cli（开批即开路径留痕），加载登录态文件。不混开两套 | 否 |
| 必须看画面：canvas、游戏前台、视觉核对 | Playwright 的页面截图，无头即可。用户要实时看或接手时，才开自启有头窗口 | 否 |
| 只能用保险库填表的账号；登录要用户接管 | 平台自带桌面 Chrome | 是 |

只有这些情况才过代理或开平台自带桌面浏览器：必须用保险库填表或用户接管登录；或者同一地址直连已经证实失败（例如已记录的 TLS 失败），才允许对该地址改走 8791，并写明原因。不要改平台桌面浏览器的代理设置，也不要重启相关平台进程。

走代理或开平台桌面 Chrome 之前，必须先在当前聊天提醒用户，说明原因。没提醒不得开工。看画面优先用 Playwright 的页面截图，无头即可；不要为了看页面或避免卡顿去改平台 Chrome 配置，也不要为此打开平台 Chrome。用户要实时看或接手时，才开自启的直连有头窗口。（2026-11-11 用户确认）

## 执行方交接（2026-11-09 纠正）

原「UI自动化协调」（id: 7f9ec681-8410-4441-9d55-95df8a2e4cad）已改名为「自动化踩坑知识库」。取消「探路交给 UI自动化协调」。该 id 不再做 UI 探路、不写/改 Playwright 脚本与选择器、不日常连跑。

UI 探路与写脚本：由各项目执行方自己处理。选型见本技能，默认 [playwright-cli](sand-workflow:playwright-cli)。必要时 Cursor 协助。

自动化踩坑沉淀：遇到问题并解决后，把脱敏汇总交给「自动化踩坑知识库」（同 id）：项目名、现象、已尝试步骤、最终解法或仍未解原因、脱敏证据路径。禁止凭证。该库只沉淀可复用知识，不替执行方排障到底，也不接连跑。

框架级新设计仍先 Cursor 审核。T8T 自动化框架要推进，不要写成暂不推进。

## 选型（按优先级）

1. **有连接器或 API**：用 MCP/接口，不点页面。
2. **可重复回归**：只跑仓库 Playwright 脚本（或 Playwright MCP 复跑）。下次只跑脚本。
3. **网页探路与一次性走查**：默认用 **[playwright-cli](sand-workflow:playwright-cli)**，**不要混开两套抢同一测号会话**。
   - **[playwright-cli](sand-workflow:playwright-cli)**（默认）：Shell 驱动、`-s=<项目短名>` 会话隔离。开批即 `tracing-start`（screenshots 和 snapshots 都开），收批 `tracing-stop`，产出带步骤和页面快照的路径留痕。
   - **Playwright MCP**：只用于不需要路径留痕的快速查看。不要为了补 trace 去改连接器启动参数，除非用户明确要求。
   - **[agent-browser](sand-workflow:agent-browser)**：备用。它的 trace 是 Chrome 开发者工具的 json，不算路径留痕。
4. **本地 Web 应用/dev server**：可加载 [webapp-testing](sand-workflow:webapp-testing)（先侦察再动作、`networkidle`、with_server）。远程业务站仍走第 3 条。
5. **探路跑通后固化**：能复用的操作或测试用例都要写成复用脚本，脚本要边测边改。当场用 `generate-locator` 或 `recording-stop` 写成 Playwright 脚本落盘（角色/可访问名定位，开 trace）。第二次起回到第 2 条。写脚本时可加载 `modern-web-guidance`。
6. **必须看画面**（canvas、游戏前台、视觉核对）：优先用 Playwright 的页面截图，无头即可。用户要实时看或接手时，再开自启直连有头窗口。不要为此打开平台自带桌面浏览器。画布、游戏画面、图表等读不到按钮结构时，改走 [canvas-ui-testing](sand-workflow:canvas-ui-testing)；普通页仍先读结构树再配截图。独立浏览器和网页工具都够不到时（原生桌面等），才用 computerUse 操作桌面本身。要走 8791 代理或开平台 Chrome 时，先提醒用户。
7. **禁止**：用 Shell 的 xdotool、CDP、Playwright 去驱动机器人电脑**自带桌面浏览器窗口**（平台边界）。playwright-cli / agent-browser / 仓库 Playwright 跑的是独立浏览器或目标站点，不等于操控桌面 Chrome。

## 有头、无头和 Playwright Extension（2026-11-21 Asia/Shanghai 实测）

实测环境：云电脑上的 Google Chrome for Testing 158（配置目录 `~/.config/chrome-direct`），用 playwright-cli 对比无头自己开浏览器、有头调试端口直连、Playwright Extension 连接。测试页标题 CMP-EXT-20261121-1641。

1. 边测边改脚本、不用盯画面：用无头。脚本自己开浏览器，实测约 1 秒起来；登录再点操作一轮约 2.5 秒；改完再跑一条约 0.8 秒。不用点「允许连接」。登录态用 playwright-cli 的 state-save / state-load 复用，不必靠插件。
2. 要盯着看、边改边看页面：开有头 Chrome for Testing（配置目录 `~/.config/chrome-direct`，启动参数见云电脑 `/workspace/qa/bin/browser_defaults.py` 的 `persistent_context_kwargs`）。连上之后，改一条再跑的速度和无头同一量级（实测约 0.8–1.2 秒）。
3. 接已经打开、已经登录的有头窗口：优先用 Chrome for Testing 的调试端口直连（`playwright-cli attach --cdp`）。实测有头约 0.9 秒、无头约 0.6 秒，能直接看到当前页，不用点允许。只接我们自己拉起的 Chrome for Testing，禁止用 CDP / Playwright / xdotool 去接或驱动平台那只桌面 Chrome（通常调试端口 9224、强制走 8791 代理）。
4. Playwright Extension（Chrome Web Store id `mmlmfjhmonkocbjadbfplnigmagldckm`，官方解包副本在云电脑 `/workspace/qa/browser-extensions/playwright-extension`）也可接已打开的有头窗口。Chrome for Testing 不能从商店装扩展，有头直连窗口启动时加载这份官方副本；无头回归不加载。配好自动连接 token 后约 1 秒能连上；不配要在「Connect to Playwright」页点允许。自动连上后默认往往是空白页，登录态还在，但不会自动停在原来盯着的那一页，还要再打开对应地址。不要把 token 写进仓库、聊天或技能正文。
5. 无头不要走这个插件：扩展能加载，但 attach 连不上。没有可点的连接页，带上 token 等了 20 秒也没连上。无头复用登录态用 state-save / state-load，或对自己拉起的无头 Chrome for Testing 走调试端口直连。

## 不抢浏览器，改脚本复用页面（2026-11-26）

1. 测试执行不要抢浏览器：禁止接或驱动平台桌面 Chrome；同一登录号同一时间只开一种探路工具，不要混开两套抢同一测号会话。
2. 改脚本不要每次重新开页面、重新登录。优先复用已打开的页面和已保存的登录态。
3. 边测边改、不用盯画面：用无头；登录态用 playwright-cli 的 `state-save` / `state-load` 复用。
4. 要盯着看：自己拉起有头 Chrome for Testing（配置目录 `~/.config/chrome-direct`），用 `playwright-cli attach --cdp` 接到调试端口，改一条再跑，直接看当前页。只接自己拉起的 Chrome for Testing。
5. 正式复测或回归下结论，仍须进入当前环境当轮现取证，不得拿以前的截图或旧数据当结论；这不妨碍改脚本时复用当轮已打开的页面和登录态文件。

## 先认机器，再选这台上效率最高的方式（2026-11-26）

默认追求效率最高，但不要套死一套工具。先认清当前是哪台机器、什么系统、这台上已有什么，再选最合适且效率最高的方式。不能只说「本地」，要写机器标识。Linux 云电脑和 Windows 本机不能混用路径和命令；macOS 或其他架构也先探再选，不要套现成路径。同一账号下的不同电脑要换机器重新探。各台的 Node、CLI、浏览器版本不必跨机器对齐。登录态和调试端口只属于当前这台机器，不能跨机器、跨系统用。8791 是云电脑桌面浏览器的问题，不要套到用户电脑。用户电脑本身需要的 VPN 或系统代理不要盲目关掉。有头启动按系统分开：Windows 本机有真实桌面，但仍不抢、不驱动用户正在用的系统 Chrome；Linux 云电脑用 `/workspace/qa/bin/open_direct_headed.py` 拉起后再 attach。Linux 上启动 Chrome for Testing 常需要 `--no-sandbox`，Windows 一般不这样套。环境配置要写明机器标识、系统、版本和路径，不要只写「环境已就绪」。用前先探，路径和版本记在本机，不抄到别的机器。Cursor 也必须遵守。

探环境至少看这些，缺什么再补什么，已经能用的不要重装：机器标识、系统与架构、shell 是 PowerShell 还是 bash；Node / npm 是否在当前终端的 PATH 里；是否已有 playwright-cli、Python Playwright，以及 ms-playwright 是否完整；Chrome for Testing 与 headless shell 的目录名按系统分开，Linux 是 chrome-linux64，Windows 是 chrome-win64，不能混用；系统 Chrome 或平台桌面 Chrome 只记录，禁止驱动；当前是否已有调试端口、登录态和仍可用的浏览器会话。云电脑用 bash，开工先跑 `/workspace/qa/qa-ready.sh`，缺了才补，不跑 apt，不全量重装。Windows 用 PowerShell，不要用 bash 的 `&&`、`mkdir -p`，按本机已有的包管理方式补缺的那几样。给哪台机器下命令，就只对那台机器。

## playwright-cli 要点

- 务必 `-s=<项目短名>`，默认会话会互相踩
- 开批：`tracing-start`（screenshots 与 snapshots 都开）。收批：`tracing-stop`，产物进本批目录
- 核心：`open` → `snapshot`（需要编号和位置时加 `--boxes`）→ 按 ref `click/fill eN` → `requests`/`console` → `close`
- 辅助：大页用 `find <文案>` 搜节点；`highlight eN` 把目标描出来对照；跑通后 `generate-locator eN` 或 `recording-stop` 当场落脚本。不要猜像素坐标。这就是「SoM / 标号截图」的官方做法，不要另装 SoM 框架。普通页不要开 Playwright MCP vision。
- 详情见 [playwright-cli](sand-workflow:playwright-cli)
- M3、T8T、GO 用自启的直连浏览器，无头为默认；需要人眼或 computerUse 看时再用自启有头直连窗口。批次记录写一行「直连 / 无头或有头」。不要为此打开平台自带桌面浏览器

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

1. **识别**：按本技能选型取树，默认 playwright-cli `snapshot`（需要编号和位置时加 `--boxes`）。拿到控件 ref、role、name 和可选的 `[box=…]`。必须看画面时再配 Playwright 页面截图。禁止一上来猜坐标。动作只点 ref / role / testId。这就是文中「SoM / 标号截图」的官方做法，不要另装 SoM 框架。画布页改走 [canvas-ui-testing](sand-workflow:canvas-ui-testing)。
2. **跑通**：按业务步骤用 ref 点击、填表、断言。每步动作后验状态（URL/文案/控件）。可挂接口监听区分前后端。
3. **自愈**：同一步最多试 ① 项目库选择器 ② a11y role/name ③ 结构树可见文案（可用 `find`，必要时 `snapshot --boxes` 对照编号）。全失败则 fail-closed，记缺口，禁止连点乱试。
4. **落脚本（必做）**：能复用的操作或测试用例都要写成复用脚本，脚本要边测边改。流程首次完整跑通后，**当场**用 `generate-locator` 或 `recording-stop` 生成 Playwright 脚本（或补进现有 spec），写入本项目约定目录，步骤带知识点/用例编号注释。选择器写入本项目选择器库。写脚本时可先加载 `modern-web-guidance`。
5. **复用**：同一流程第二次起只跑脚本。脚本失败再探路修复，修完立刻更新脚本，不长期靠 MCP/CLI 手点。
6. **升级门槛**：连续成功 ≥2 次或用户明确要回归的路径，必须已有脚本，否则算未完成。

脚本最低要求：稳定定位（优先 getByRole/getByTestId）、关键断言有依据、失败出 trace/截图路径、不用硬编码密钥。

## 实时自愈（探路必做）

1. **先读后点**：先 `snapshot`（必要时 `--boxes`）再行动，按 ref 点，不猜像素。
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

1. 网页探路默认 playwright-cli。不要因为对话超过两轮就改派 computerUse。只有独立浏览器和网页工具都够不到时（原生桌面等），才用 computerUse 操作桌面本身。
2. 不轮询 CheckSubagent。
3. 同时只跑一个 computerUse。
4. 站点有 `site-playbooks-*` 时先加载。
5. 开浏览器前不检查内存、不跑体检、不等待。失败立刻报告，带上 trace 或截图、`python3 /workspace/qa/bin/box_health.py` 输出的前几行，以及 `/proc/vmstat` 的 oom_kill 计数。体检是失败后的取证，不是开前的门。电脑桌面本身坏了，再考虑 [Update Bot's Computer](grokbot://app/v1/settings?id=update-computer)。

## 批次目录、检查点与接口优先

1. 每批一个目录，固定放：范围与验收标准、trace、请求摘要、控制台、截图、结果表。证据在跑的过程中自动产生；收工只补判定依据和异常。稳定步骤可写「同上次，无变化」。
2. 每条用例跑完即落盘状态。失败后从已验证检查点续跑，先核实前置状态。续跑是报告之后的决定，不是自动重试。
3. 能用接口验的先用接口批量验，UI 只验接口验不了的部分。接口走仓库脚本加项目 `.env`，结果进批次目录。每个流程至少保留一条 UI 主路径。「接口通过」不能写成「功能通过」；没跑 UI 的写「未测」。
4. 只有功能本身有实时消息推送时，才用 Playwright 脚本监听 `websocket` / `framesent` / `framereceived`，写入该批次目录。探路命令不做这项留痕。
