---
name: e2e-debugger
description: >-
  Playwright/Cypress 自动化用例失败或 flaky 时使用。先连跑区分
  flaky，再判定应用回归/用例缺陷/环境，只修测试且不削弱断言，不改产品代码。
---
# E2E 调试（机器人优化版）

调试失败或 flaky 的自动化用例。不写新用例、不审已通过用例。不扩大项目授权。

## 安全

1. 一次只盯一个具名失败用例（文件 + 标题）
2. 只改测试文件（spec/helper/fixture/page object）。不改产品代码、不改 CI 配置、不改快照基线除非用户点名
3. 禁止削弱断言：不加 skip/fixme/only、不加长 timeout 当修复、不用 `force: true` 糊弄、不删断言
4. 凭证走 Vault。不读不打印 `.env` / auth.json 明文到聊天
5. 目标环境必须是本项目已授权测试/staging。生产拒绝。远程测站可以，不限于 localhost
6. 最多两轮修复尝试。仍红则停并报告

## 1. Flake 检查

隔离到该用例后连跑 3 次，关闭重试：

- Playwright：`--repeat-each=3 --retries=0`
- 结果混杂 → **FLAKY**，只报证据，先不改代码（除非用户明确要稳 flaky）
- 三次全绿 → **未复现 / UNCLEAR**，停
- 三次全红 → 继续定性

## 2. 定性

结合失败断言、用例要守的要求（标题/注释/知识点/用户点名）、近期改动：

- **APP-REGRESSION**：应用不再满足断言所守要求 → 不改产品也不改测试，出缺陷候选 + 证据
- **ENV**：环境/账号/baseURL/浏览器 → 不改代码，报阻塞
- **UNCLEAR**：证据不足以证明测试错 → 不改
- **TEST-DEFECT**：应用满足要求、测试错（过时定位、错数据、坏 helper）→ 进入修复

可先加载 [playwright-report-triage](sand-workflow:playwright-report-triage) 读本跑次产物。

## 3. 修测试缺陷

1. 定位器只换成指向同一意图元素的更稳写法（role/testId 优先）
2. 期望值只在用户/知识点明确改要求时才改
3. 修完再连跑 3 次须全绿
4. 仍失败：回滚本次测试改动，报 UNCLEAR

## 4. 输出

短句中文：

```text
分类：FLAKY | APP-REGRESSION | TEST-DEFECT-FIXED | ENV | UNCLEAR
证据：三次结果、错误原文、报告/trace 路径
改动文件：仅测试侧或无
未做：未改产品、未加长等待装通过
```

故障仍按协作技能报总控。踩坑脱敏汇总可交「自动化踩坑知识库」。
