---
name: automation-regression
description: >-
  写或跑 UI/API 自动化回归、核对需求与实现是否一致时使用。约定仓库 Playwright 脚本做 UI、Postman/OpenAPI
  做契约、用例挂知识点。预期必须有依据。探路选型见 box-ui-speed，默认 playwright-cli。可重复路径禁止桌面点屏。踩坑卡片字段见
  ui-auto-coordinator。定位器可自愈；需求已写明或资金账务不得按现状改断言，需求没写清且非这两类可按实测改并标明依据。断言优先核对业务结果，不要只断言元素还在。
---
# 自动化回归（UI / API / 需求一致性）

通用模板。项目入口、测号、知识库、审批边界以该机器人职责与本项目知识库为准，本技能不扩大授权。

用户说重新测试或回归时，当轮现取证见 [测试证据](sand-workflow:skill-1794740098289)「重新测试或回归」。本技能不另定通过或失败。

## 何时加载

- 要写或改 UI/API 自动化
- 要跑回归并出可追溯结果
- 要核对「需求/知识点」与实现或用例是否一致
- 要按 box-ui-speed 探路并自动落脚本

## 执行方交接（2026-11-09 纠正）

原「UI自动化协调」（id: 7f9ec681-8410-4441-9d55-95df8a2e4cad）已改名为「自动化踩坑知识库」。取消「探路交给 UI自动化协调」。该 id 不再做 UI 探路、不写/改 Playwright 脚本与选择器、不日常连跑。

UI 探路与写脚本：由各项目执行方自己处理。选型见 [box-ui-speed](sand-workflow:box-ui-speed)，默认 [playwright-cli](sand-workflow:playwright-cli)。必要时 Cursor 协助。

自动化踩坑沉淀：遇到问题并解决后，把脱敏汇总交给「自动化踩坑知识库」（同 id）：项目名、现象、已尝试步骤、最终解法或仍未解原因、脱敏证据路径。禁止凭证。该库只沉淀可复用知识，不替执行方排障到底，也不接连跑。

框架级新设计仍先 Cursor 审核。T8T 自动化框架要推进，不要写成暂不推进。

## 默认技术选型

1. UI 探路：见 [box-ui-speed](sand-workflow:box-ui-speed)，默认 [playwright-cli](sand-workflow:playwright-cli)。优先 a11y snapshot + ref。不混抢同一测号。
2. UI 回归：仓库 Playwright 脚本（优先 getByRole / getByTestId，开 trace）
3. API：Playwright `APIRequestContext` 或 Postman，与 UI 共享登录态与报告
4. 契约：OpenAPI/Collection。需要时加载 `api-testing`、`application-testing`、`ci-integration`、`collection-schema-v3`，也可参考 [api-contract-testing](sand-workflow:api-contract-testing)（若已装）
5. 本地 Web/dev server：可加载 [webapp-testing](sand-workflow:webapp-testing)
6. 不做生产真实资金写操作。凭证走 Vault，不进聊天、Notion、记忆或仓库明文
7. 默认直连，不经 `127.0.0.1:8791` 代理。路线表见 [box-ui-speed](sand-workflow:box-ui-speed)。不要给独立浏览器设置该代理。只有必须用保险库填表、要用户接管登录，或同一地址直连已证实失败时，才开平台自带桌面浏览器。
8. 有头、无头和 Playwright Extension 怎么选，见 [box-ui-speed](sand-workflow:box-ui-speed)「有头、无头和 Playwright Extension」。

## Modern Web Guidance（仅探路写脚本）

1. 用户已装 Modern Web Guidance（插件 6398877）。写或修补 Playwright 脚本、选择器策略时，可先加载 `modern-web-guidance`。
2. 只指导现代 Web 与稳定定位写法。不替代脚本回归执行，不替代接口契约与证据门禁，不进入正式连跑主循环。
3. 优先 role/label/testId 与有依据断言。少脆弱纯 CSS 与猜坐标。

## 自动识别 → 自动跑 → 自动写脚本

1. 探路按 [box-ui-speed](sand-workflow:box-ui-speed) 读 snapshot，用 ref 跑通主路径
2. 首次跑通后**当场**生成/更新 Playwright 脚本到本项目约定目录，步骤注释挂知识点编号。写脚本时可加载 `modern-web-guidance`
3. 选择器写入本项目选择器库。第二次起只跑脚本
4. 脚本失败再探路修复，修完立刻更新脚本。只许当场自愈定位器（只换更稳的同意图定位，优先 role / testId）。断言按「预期结果必须有依据」处理，不能在当次失败里悄悄改期望当通过
5. 用户要回归或路径已稳定时，没有脚本算未完成

## 手测转脚本短路径（v1，2026-11-10，用户批准）

与上段时机不一致时以本段为准：首次跑通可以当场落脚本，最迟第二次必须落。

2026-11-22 用户确认：能复用的操作或测试用例都要写成复用脚本，脚本要边测边改。与上一句时机不一致时，能复用的以这句为准，同一路径最迟第二次仍必须落成脚本。UI 用例和接口用例注明哪些走 UI、哪些走接口。

1. 第一次手测留痕，放本项目自己的目录
2. 能复用的当次落成脚本，并边测边改。同一路径最迟第二次落成本项目脚本，断言挂已确认 K 编号。没有已确认编号的断言标待确认，不当通过依据
3. 第三次起只跑脚本，不再手点
4. 脚本目录按项目隔离：/workspace/ui-auto/<项目>/。M3 与 M3+支付 选择器分开放，不共用一份选择器库。AntPay 库建成前不写 AntPay 脚本
5. 失败先按现象查「自动化踩坑知识库」（id: 7f9ec681-8410-4441-9d55-95df8a2e4cad）。命中就沿用旧解法，回报写卡片名。没命中再探路
6. 结案补卡片交踩坑库：字段见 [ui-auto-coordinator](sand-workflow:ui-auto-coordinator)（问题、改法、结果、仍未证明什么），带 Cursor 案例号或 PR 链接。卡片不写脚本正文，不写凭证
7. 收工时记两数给日报周报：命中旧卡次数、新建卡次数。取不到写未统计

## 路径提速（防卡顿）

1. 可重复用例必须脚本化，禁止 computerUse 当回归执行器
2. 探路加载 [box-ui-speed](sand-workflow:box-ui-speed) 的实时自愈与落脚本规则
3. 能 API 断言的不要先点 UI
4. 定位与控件状态见 `ui-interaction-kit`
5. 测试执行不抢浏览器，不驱动平台桌面 Chrome，不混开两套工具抢同一测号会话。改脚本复用已打开的页面和登录态（`state-load` 或 `attach --cdp` 接到自己拉起的 Chrome for Testing），不要每次重新开页面。细则见 [box-ui-speed](sand-workflow:box-ui-speed)
6. 先认清当前是哪台机器、什么系统、这台上已有什么，再选最合适且效率最高的方式。不能只说「本地」，要写机器标识。Linux 云电脑和 Windows 本机不能混用路径和命令；macOS 或其他架构也先探再选，不要套现成路径。同一账号下的不同电脑要换机器重新探。各台的 Node、CLI、浏览器版本不必跨机器对齐。登录态和调试端口只属于当前这台机器，不能跨机器、跨系统用。8791 是云电脑桌面浏览器的问题，不要套到用户电脑。用户电脑本身需要的 VPN 或系统代理不要盲目关掉。有头启动按系统分开：Windows 本机有真实桌面，但仍不抢、不驱动用户正在用的系统 Chrome；Linux 云电脑用 `/workspace/qa/bin/open_direct_headed.py` 拉起后再 attach。Linux 上启动 Chrome for Testing 常需要 `--no-sandbox`，Windows 一般不这样套。环境配置要写明机器标识、系统、版本和路径，不要只写「环境已就绪」。用前先探，路径和版本记在本机，不抄到别的机器。细则见 [box-ui-speed](sand-workflow:box-ui-speed)。

## 预期结果必须有依据（准确性）

断言优先核对业务结果（跳转、金额、状态、关键文案），不要只断言某个控件还在或按钮消失了。控件状态可作补充，不能单独代替业务结果。

1. 每条用例预期必须能指到需求/知识点/原型/契约/规则/已确认缺陷结论或可核验证据
2. 禁止凭感觉写期望。缺依据先补来源
3. 报告附依据编号或链接。无依据标待确认
4. 与有依据预期不一致记缺陷候选。依据冲突先问清
5. 脚本或探路失败时，只许当场自愈定位器（只换更稳的同意图定位，优先 role / testId）。需求已经写明或属于资金账务：页面不符就是缺陷，不许为跑绿改断言、删断言或放宽断言，也不能只靠页面现状当成上线通过。需求没写清，又不是资金账务或需求里已经写明的点：可按页面实际改断言，必须标明「实测归纳」并写清思考依据，先改用例和断言再重跑。不能在当次失败里悄悄把期望改成现状就算通过。需求已明确变更时，同样先改用例和断言再重跑。

## 需求与实现一致性

1. 开工先加载本项目测试记忆-开工技能
2. 用例标题或 tag 带知识点/需求编号
3. 改动先加载影响面技能再补测
4. 报告能按编号回答覆盖、缺口、不一致点
5. 资金类优先：金额精度、幂等、状态机、超时、对账字段

## 落地顺序

1. 锁契约
2. API 冒烟
3. 网页探路主路径并落脚本（见 box-ui-speed）
4. 脚本回归 + 回挂知识点。缺陷候选先确认再存档

## 失败读报告

1. 只读本项目 HTML report / trace / 截图 / 接口摘要
2. 区分前端与接口失败。加载 [playwright-report-triage](sand-workflow:playwright-report-triage)（若已装）
3. 无证据不算测过。诚实写通过/失败/阻塞/未测

## 输出

短句中文，先结论。给出通过/失败/未跑、脚本路径、选择器是否固化、失败证据、未覆盖编号、预期依据。不编造未跑结果。

## 故障

仍按《项目机器人协作与故障闭环》报总控，本技能不代替排障授权。
