---
name: browser-qa
description: 对已部署的前台/后台做发布后冒烟与交互走查时使用：console 与网络、关键路径点击、多断点截图、无障碍抽检，给出有证据的结论。默认只读，不碰资金写操作。
---
# Browser QA（机器人优化版）

对 staging / 测试环境已部署页面做冒烟与交互核对。不扩大项目授权，不跨项目借测号。

## 何时用

- 发布后或预览环境要快速核对 UI 是否可用
- 前端改动后需要 console / 网络 / 关键路径证据
- 需要多断点截图或无障碍抽检

正式回归、可重复路径仍以仓库 Playwright 脚本为准，并加载 [automation-regression](sand-workflow:automation-regression) 与 [box-ui-speed](sand-workflow:box-ui-speed)。

## 工具选型

网页探路三选一（不混抢同一测号）：Playwright MCP、[playwright-cli](sand-workflow:playwright-cli)、[agent-browser](sand-workflow:agent-browser)。桌面/canvas 才用 computerUse。

## 安全边界

1. 默认只读。充值、提现、下注、领奖、绑卡、删数、生产真实资金写操作禁止
2. 凭证走 Vault / sign-in。不进聊天、Notion、记忆、截图明文
3. 截图与 HAR 先脱敏再外发。可参考 [evidence-hygiene](sand-workflow:evidence-hygiene)
4. 目标 URL 必须是本项目已授权环境。不确定就先问

## 阶段 1：冒烟

1. 打开目标 URL
2. 看 console：过滤分析/第三方噪音，记关键错误
3. 看网络：有无 4xx/5xx（本项目关注接口）
4. 首屏截图（桌面断点）
5. 可选：LCP/CLS 等性能抽检，无工具则标未测

## 阶段 2：交互

1. 主导航与关键入口可点通
2. 表单：有效输入看成功态，无效输入看错误态（有依据才写期望）
3. 登录流：仅测号，登录→受保护页→退出（若任务授权）
4. 关键业务路径按任务清单，不擅自扩测

## 阶段 3：视觉抽检

1. 关键页 375 / 768 / 1440 截图（按任务需要，不必全量）
2. 无基线则标「无基线，无法视觉对比」，禁止静默写通过
3. 明显溢出、缺控件、错位记缺陷候选

## 阶段 4：无障碍抽检

1. 有 axe 或等价工具再跑。没有则标未测
2. 自动化通过不等于无障碍通过。键盘与焦点另记

## 输出

短句中文，先结论。模板：

```text
结论：通过 / 有问题可带病 / 不建议放行 / 证据不足
冒烟：console、网络、首屏证据路径
交互：逐条 ✓/✗/未测 + 依据
视觉：有无基线、问题点、截图路径
无障碍：结果或未测
待用户确认的缺陷候选：…
```

无证据不算测过。不编造未跑结果。
