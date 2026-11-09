---
name: playwright-report-triage
description: 读本项目 Playwright HTML report、trace、截图或失败日志做分诊时使用。只根据本跑次产物下结论，区分前端与接口，不编造未打开的附件。
---
# Playwright 报告分诊（机器人优化版）

只处理**本项目**回归产物。不要去查微软 Playwright 上游 CI DuckDB。

## 何时用

- 脚本回归失败要快速定性
- 用户丢来 report 目录 / trace.zip / 失败截图
- 需要区分 flaky、环境、断言、接口还是选择器

## 输入

按优先级打开：

1. HTML report（`playwright-report/index.html` 或项目约定路径）
2. `test-results/**/trace.zip`（`npx playwright show-trace` 或解压读）
3. 失败截图与 error-context.md
4. 接口监听摘要 / HAR（已脱敏）

路径以本项目约定为准。找不到就写「未找到报告」，不要猜。

## 分诊步骤

1. 记下：用例名、项目/浏览器、重试次数、最终 status
2. 读错误消息与堆栈：断言失败 vs timeout vs 选择器丢失 vs 页面崩溃
3. 有网络面板或 requests 日志时：关键请求 status/body 是否先失败
4. 对比前后步骤截图：是没点到还是点到了后端错
5. 重试曾绿：标 flaky 候选，附次数，不直接当通过

## 结论标签

- 前端/选择器
- 接口/契约
- 环境/账号/权限
- 用例/期望无依据
- flaky
- 证据不足

## 输出

短句中文：

```text
结论：<标签>
失败用例：…
直接证据：路径 + 一句
是否接口先失败：是/否/未抓到
建议下一刀：修选择器 / 查接口 / 补依据 / 重跑一次
未打开的附件：列出来
```

无证据不算测过。缺陷候选先过项目过滤再入库。
