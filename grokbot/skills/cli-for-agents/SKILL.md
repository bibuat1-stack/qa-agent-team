---
name: cli-for-agents
description: 设计或评审给机器人用的 CLI 时使用：非交互优先、分层 --help 带示例、stdin/管道、可行动错误、幂等、dry-run、结构可预测。
---
# CLI for agents（机器人优化版）

给人用的 CLI 常会卡住机器人：交互菜单、超长说明书、没有可复制示例。优先无头、可管道组合的模式。

## 非交互优先

- 每个输入都能用 flag 表达。不要依赖方向键菜单或限时提示
- 缺 flag 时再退回交互，不要反过来

坏：`mycli deploy` → 箭头选环境  
好：`mycli deploy --env staging`

## 可发现且不灌上下文

- 机器人分层发现：`mycli` → `mycli deploy --help`
- 不要每次打印整本手册

## `--help` 要能用

- 每个子命令有 `--help`
- 每个 `--help` 含 **Examples** 与真实调用

## stdin / 管道

- 合适处接受 stdin
- 支持链式：`mycli deploy --env staging --tag $(mycli build --output tag-only)`

## 失败要快且可行动

缺必填 flag：立刻退出，给正确示例调用，不要挂起。

## 幂等与破坏性

- 成功命令重跑应安全（noop 或明确 already done）
- 破坏性动作提供 `--dry-run`，以及 `--yes`/`--force` 跳过确认（默认对人仍安全）

## 结构可预测

统一 `resource` + `verb`。成功输出给机器可用的 id/url/duration。

## 评审清单

非交互路径、分层 help、示例、stdin、带调用示例的错误、幂等、dry-run、确认绕过、命令形状一致、结构化成功输出。

与本环境已装 CLI 对齐时：优先看 [playwright-cli](sand-workflow:playwright-cli)、[agent-browser](sand-workflow:agent-browser) 是否已满足上述习惯。
