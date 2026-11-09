---
name: accessibility
description: 做无障碍审计、WCAG 2.2 核对、键盘/读屏抽检、对比度与焦点问题时使用。用户说 a11y、无障碍、WCAG、键盘导航、读屏、可访问性时优先加载。与 browser-qa 的「无障碍抽检」互补；正式修复与回归仍跟项目授权走。
---
# Accessibility（机器人优化版）

基于 Addy Osmani web-quality-skills 的 WCAG 2.2 指南，适配本团队探路工具。不扩大项目授权；凭证不进技能正文。

## 何时用

- 用户要无障碍审计、a11y、WCAG、键盘可达、读屏、对比度、焦点可见
- [browser-qa](sand-workflow:browser-qa) 抽检发现可疑后要加深核验
- 写或评审含 axe / ARIA / 表单标签的 Playwright 断言

## 工具选型（本环境）

优先已有探路栈，**不要假设已装 Chrome DevTools MCP**：

1. Playwright MCP / [playwright-cli](sand-workflow:playwright-cli) / [agent-browser](sand-workflow:agent-browser)：取 a11y 树、键盘 Tab、截图
2. 有 axe 或 `@axe-core/playwright` 再跑自动化；没有则标「未测自动化 a11y」
3. 可选：`npx lighthouse <url> --only-categories=accessibility`（公开页或已授权 URL）

桌面/canvas 才用 computerUse。正式可重复路径以仓库脚本为准。

## 安全边界

1. 只测本项目已授权环境与测号
2. 凭证走 Vault / sign-in；不写进技能、记忆、截图明文
3. 证据外发前走 [evidence-hygiene](sand-workflow:evidence-hygiene)
4. 默认只读；资金写操作禁止

## 证据优先流程

1. 打开目标页，抓 accessibility tree（名、角色、状态、地标、标题层级）
2. 有自动化工具则跑 axe / Lighthouse a11y，记下失败节点
3. 键盘走关键路径：Tab 顺序、Enter/Space、有无陷阱、焦点是否被 sticky 挡住
4. 人工核对：对比度嫌疑、缺 label、图标按钮无名、仅靠颜色表达错误
5. 修复后（若任务含修）重跑同一审计；只审计则输出问题清单与证据路径

自动化满分 ≠ WCAG 符合。分数不能代替逐条问题证据。

## WCAG 速记（POUR）

| 原则 | 要点 |
|------|------|
| Perceivable | alt、对比度、字幕/文稿、不只靠颜色 |
| Operable | 键盘可达、焦点可见、无陷阱、目标 ≥24×24、拖拽有替代 |
| Understandable | lang、一致导航、表单标签、错误提示与 aria-invalid |
| Robust | 优先原生控件，少造 ARIA；动态内容用 live region |

目标默认 **AA**。细节与代码样例见 `references/WCAG.md`、`references/A11Y-PATTERNS.md`。

## 输出

短句中文，先结论：

```text
结论：通过 / 有问题可带病 / 不建议放行 / 证据不足
范围：URL + 视口
自动化：axe/Lighthouse 结果或未测
键盘/焦点：✓/✗/未测 + 证据
严重问题：Critical / Serious 列表（对照源技能 impact）
证据路径：截图 / 树快照 / 报告
```

无证据不算测过。不编造未跑结果。

## 来源

改编自 `addyosmani/web-quality-skills@accessibility`（MIT）。上游全文在 `~/.agents/skills/accessibility/SKILL.md`。
