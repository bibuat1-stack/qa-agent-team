---
name: automation-regression
description: >-
  写或跑 UI/API 自动化回归、核对需求与实现是否一致时使用。约定 Playwright MCP/脚本做 UI、Postman/OpenAPI
  做契约、用例挂知识点。预期必须有依据。探路与写脚本自理，可重复路径禁止桌面点屏，踩坑脱敏汇总交「自动化踩坑知识库」。
---
# 自动化回归（UI / API / 需求一致性）

通用模板。项目入口、测号、知识库、审批边界以该机器人职责与本项目知识库为准，本技能不扩大授权。

## 何时加载

- 要写或改 UI/API 自动化
- 要跑回归并出可追溯结果
- 要核对「需求/知识点」与实现或用例是否一致
- 要用 Playwright MCP / playwright-cli / agent-browser 探路并自动落脚本

## 执行方交接（2026-11-09 纠正）

原「UI自动化协调」（id: 7f9ec681-8410-4441-9d55-95df8a2e4cad）已改名为「自动化踩坑知识库」。取消「探路交给 UI自动化协调」。该 id 不再做 UI 探路、不写/改 Playwright 脚本与选择器、不日常连跑。

UI 探路与写脚本：由各项目执行方自己或既有授权方式处理（Playwright MCP、[playwright-cli](sand-workflow:playwright-cli)、[agent-browser](sand-workflow:agent-browser)、[box-ui-speed](sand-workflow:box-ui-speed)、必要时 Cursor 协助）。

自动化踩坑沉淀：遇到问题并解决后，把脱敏汇总交给「自动化踩坑知识库」（同 id）：项目名、现象、已尝试步骤、最终解法或仍未解原因、脱敏证据路径。禁止凭证。该库只沉淀可复用知识，不替执行方排障到底，也不接连跑。

框架级新设计仍先 Cursor 审核。T8T 新框架/试点按既有用户决定暂不推进。

## 默认技术选型

1. UI 探路：Playwright MCP **或** [playwright-cli](sand-workflow:playwright-cli) **或** [agent-browser](sand-workflow:agent-browser)（三选一，不混抢同一测号）。优先 a11y snapshot + ref
2. UI 回归：仓库 Playwright 脚本（优先 getByRole / getByTestId，开 trace）
3. API：Playwright `APIRequestContext` 或 Postman，与 UI 共享登录态与报告
4. 契约：OpenAPI/Collection。需要时加载 `api-testing`、`application-testing`、`ci-integration`、`collection-schema-v3`，也可参考 [api-contract-testing](sand-workflow:api-contract-testing)（若已装）
5. 本地 Web/dev server：可加载 [webapp-testing](sand-workflow:webapp-testing)
6. 不做生产真实资金写操作。凭证走 Vault，不进聊天、Notion、记忆或仓库明文

## Modern Web Guidance（仅探路写脚本）

1. 用户已装 Modern Web Guidance（插件 6398877）。写或修补 Playwright 脚本、选择器策略时，可先加载 `modern-web-guidance`。
2. 只指导现代 Web 与稳定定位写法。不替代脚本回归执行，不替代接口契约与证据门禁，不进入正式连跑主循环。
3. 优先 role/label/testId 与有依据断言。少脆弱纯 CSS 与猜坐标。

## 自动识别 → 自动跑 → 自动写脚本

1. 探路用 Playwright MCP / playwright-cli / agent-browser 读 snapshot，用 ref 跑通主路径
2. 首次跑通后**当场**生成/更新 Playwright 脚本到本项目约定目录，步骤注释挂知识点编号。写脚本时可加载 `modern-web-guidance`
3. 选择器写入本项目选择器库。第二次起只跑脚本
4. 脚本失败再探路修复，修完立刻更新脚本
5. 用户要回归或路径已稳定时，没有脚本算未完成

## 路径提速（防卡顿）

1. 可重复用例必须脚本化，禁止 computerUse 当回归执行器
2. 探路加载 [box-ui-speed](sand-workflow:box-ui-speed) 的实时自愈与落脚本规则
3. 能 API 断言的不要先点 UI
4. 定位与控件状态见 `ui-interaction-kit`

## 预期结果必须有依据（准确性）

1. 每条用例预期必须能指到需求/知识点/原型/契约/规则/已确认缺陷结论或可核验证据
2. 禁止凭感觉写期望。缺依据先补来源
3. 报告附依据编号或链接。无依据标待确认
4. 与有依据预期不一致记缺陷候选。依据冲突先问清

## 需求与实现一致性

1. 开工先加载本项目测试记忆-开工技能
2. 用例标题或 tag 带知识点/需求编号
3. 改动先加载影响面技能再补测
4. 报告能按编号回答覆盖、缺口、不一致点
5. 资金类优先：金额精度、幂等、状态机、超时、对账字段

## 落地顺序

1. 锁契约
2. API 冒烟
3. 网页探路主路径并落脚本（三选一工具）
4. 脚本回归 + 回挂知识点。缺陷候选先确认再存档

## 失败读报告

1. 只读本项目 HTML report / trace / 截图 / 接口摘要
2. 区分前端与接口失败。加载 [playwright-report-triage](sand-workflow:playwright-report-triage)（若已装）
3. 无证据不算测过。诚实写通过/失败/阻塞/未测

## 输出

短句中文，先结论。给出通过/失败/未跑、脚本路径、选择器是否固化、失败证据、未覆盖编号、预期依据。不编造未跑结果。

## 故障

仍按《项目机器人协作与故障闭环》报总控，本技能不代替排障授权。
