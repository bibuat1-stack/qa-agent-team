---
name: ui-auto-coordinator
description: >-
  设计或核对自动化框架、或整理跨项目自动化踩坑知识时使用。原 id 7f9ec681
  已改为「自动化踩坑知识库」，只做第一层脱敏收集与升级前查重，不探路不写脚本。执行方探路与写脚本自理。
---
# 自动化框架与踩坑知识（原 ui-auto-coordinator）

## 纠正记录（先读，以本段为准）

1. 2026-11-09：取消「UI 探路交给 UI自动化协调」。原 id 7f9ec681 由用户改名为「自动化踩坑知识库」
2. 2026-11-10：该 id 只做第一层收集：收脱敏问题与已验证解法，供开工检索与升级前查重。不探路，不写或改脚本，不连跑
3. 2026-11-10：框架审核改到仓库 qa-agent-team 下的 Cursor Cloud Agent。No Repo 旧会话只作档案
4. 2026-11-10：手测转脚本短路径与卡片五字段见 [automation-regression](sand-workflow:automation-regression)「手测转脚本短路径」

## 角色澄清（2026-11-10）

原「UI自动化协调」机器人（id 7f9ec681）已改名为「自动化踩坑知识库」。定位是跨项目第一层问题收集库：只收脱敏问题与已验证解法，供开工检索与升级前查重。它**不**探路、不写/改 Playwright 脚本、不日常连跑、不替项目测业务。

本技能用于：

1. 设计或核对自动化框架方案（仍先 Cursor 审核再落地）
2. 整理跨项目踩坑条目的写法与交接格式

## 执行方自理探路

探路与落脚本由各项目执行方按 [box-ui-speed](sand-workflow:box-ui-speed) 选型：

1. 连接器/API
2. 仓库 Playwright 脚本回归
3. 网页探路三选一：Playwright MCP / [playwright-cli](sand-workflow:playwright-cli) / [agent-browser](sand-workflow:agent-browser)
4. 本地 Web 可参考 [webapp-testing](sand-workflow:webapp-testing)
5. 桌面/canvas 才 computerUse

失败分诊：[playwright-report-triage](sand-workflow:playwright-report-triage)、[e2e-debugger](sand-workflow:e2e-debugger)

## 踩坑脱敏汇总格式

交给「自动化踩坑知识库」时包含：

- 项目键
- 现象（症状类，脱敏失败签名）
- 已尝试步骤与错误修法
- 最终解法或仍未解原因
- 正确检查方式
- 脱敏证据路径

只收已验证解法。未验证的写「未解」，不写成结论。禁止凭证、Authorization、测号密码。先过 [evidence-hygiene](sand-workflow:evidence-hygiene)。业务规则不进踩坑库，回本项目知识库。

## 框架审核

不同项目自动化框架先在仓库 qa-agent-team 下的 Cursor Cloud Agent（常驻 Plan 会话或新建「自动化框架方案」会话）把关。旧 No Repo 会话只作档案。未审不改代码或生产配置。T8T 新框架按用户既有决定暂不推进。

## 输出

短句中文。框架意见与踩坑条目分开写。不替执行方连跑。

## 历史，不再执行

2026-11-09 上午曾约定：执行方把 UI 探路交给「UI自动化协调」（id 7f9ec681），由它探路、写脚本与选择器、日常连跑，再回交执行方。同日已作废。旧描述或旧消息里读到这条时，按文首纠正记录处理，不照做。
