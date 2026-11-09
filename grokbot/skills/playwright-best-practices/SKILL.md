---
name: playwright-best-practices
description: >-
  写或评审 Playwright UI 自动化、选定位策略、用自动等待与 expect 断言、规避 flaky 时使用。
  与 automation-regression、box-ui-speed、e2e-debugger、webapp-testing、playwright-cli、
  agent-browser 互补；不替代探路选型与失败分诊。用户说 Playwright 最佳实践、定位器、
  auto-wait、expect、flaky 时优先加载。
---
# Playwright 最佳实践（机器人优化版）

改编自 currents-dev `playwright-best-practices`（MIT）。本技能只讲**写/改/评 Playwright 脚本**时的稳定写法；探路工具选型与回归编排仍跟既有技能。不扩大项目授权；正文不含凭证。

## 何时用

- 写或改 Playwright 用例 / Page Object / fixture
- 选定位器（role / label / testId / CSS）
- 用 `expect` 自动等待，去掉硬编码 `waitForTimeout`
- 评审脚本是否易 flaky
- 固化探路结果为可复用脚本时，补定位与断言写法

## 不覆盖（交给兄弟技能）

| 场景 | 加载 |
|------|------|
| 回归编排、预期依据、落脚本流程 | [automation-regression](sand-workflow:automation-regression) |
| 探路优先级、会话隔离、computerUse 末位 | [box-ui-speed](sand-workflow:box-ui-speed) |
| 已失败/flaky 用例分诊与只修测试 | [e2e-debugger](sand-workflow:e2e-debugger) |
| 本地 dev server / 短 Python 脚本 | [webapp-testing](sand-workflow:webapp-testing) |
| Shell 探路 CLI | [playwright-cli](sand-workflow:playwright-cli) |
| 独立 Chromium 探路 | [agent-browser](sand-workflow:agent-browser) |
| HTML report / trace 分诊 | [playwright-report-triage](sand-workflow:playwright-report-triage) |
| 无障碍审计加深 | [accessibility](sand-workflow:accessibility) |

## 工具优先级（与团队一致，勿矛盾）

1. **有 API / 连接器**：接口断言，不点 UI  
2. **可重复回归**：只跑仓库 Playwright 脚本（开 trace）  
3. **网页探路**：Playwright MCP **或** playwright-cli **或** agent-browser（三选一，不混抢同一测号）  
4. **computerUse**：仅桌面 / canvas / 网页工具够不到时  
5. 探路跑通后**当场**落脚本；第二次起回到第 2 条  

本技能作用于第 2 条与「落脚本」的写法质量，不把 computerUse 当回归执行器。

## 安全与证据

1. 只测本项目已授权环境与测号；项目隔离，不串账号  
2. 登录走 Vault / sign-in；密码、token、Cookie、测号明文不进技能、记忆、脚本硬编码、聊天  
3. **无证据不算测过**：失败须有本跑次 trace / 截图 / 报告路径；外发前 [evidence-hygiene](sand-workflow:evidence-hygiene)  
4. 不做生产真实资金写操作；预期必须能指到知识点/契约/规则  

## 定位器优先级

稳定优先，与 a11y 探路一致：

1. `getByRole`（最稳，贴近用户与读屏）  
2. `getByLabel` / `getByPlaceholder`  
3. `getByText` / `getByTitle`（注意精确匹配）  
4. `getByTestId`（语义定位不够时）  
5. CSS / XPath（最后手段；禁止靠脆弱 nth + 纯类名凑合）  

禁止一上来猜坐标或 `force: true` 糊弄。探路用 a11y snapshot / ref，固化时改成 role/name/testId。详情见 `references/locators.md`。

```typescript
// 好
await page.getByRole("button", { name: "提交" }).click();
await page.getByLabel("邮箱").fill(email);

// 差
await page.locator(".btn-primary > span:nth-child(2)").click();
await page.waitForTimeout(3000);
```

## 自动等待与断言

- **优先 web-first `expect`**：可见、可点、文案、URL 会自动重试到超时  
- **禁止**用固定 `waitForTimeout` 当同步手段；动画/淡出等稳定态用 `toBeHidden` / `toBeAttached({ attached: false })` 等条件等待  
- 动作后验状态：URL、关键文案、控件 enabled/hidden  
- 非 UI 值用普通 `expect`（不重试）；接口用 `APIRequestContext` + `expect(response).toBeOK()`  

```typescript
await page.getByRole("button", { name: "确认" }).click();
await expect(page.getByRole("dialog")).toBeHidden();
await expect(page).toHaveURL(/\/done/);
```

详情见 `references/assertions-waiting.md`。

## 防 Flaky 清单（写/评必过）

1. 不用固定 sleep；等条件不用等时钟  
2. 断言落在**稳定态**（动画结束、网络关键响应、toast 关闭后），勿在过渡帧上断言「已关闭」  
3. 用例数据隔离：不共用可变全局账号状态；并行时各用独立数据  
4. 避免依赖执行顺序；清理在 fixture / afterEach  
5. 少用 `networkidle` 当唯一门闩（长轮询页易挂）；优先具体接口或 UI 条件  
6. 正式回归**禁止**用 skip/fixme/放宽断言/加长 timeout 当「修复」——那是削弱，交给 [e2e-debugger](sand-workflow:e2e-debugger) 定性  

复现：`--repeat-each=N --retries=0`。分类与修法见 `references/flaky-tests.md`。

## 脚本最低要求（落盘）

- 稳定定位（优先 role / testId）  
- 关键断言有依据（知识点/用例编号注释）  
- 失败出 trace / 截图路径（配置 `trace: on-first-retry` 或本项目约定）  
- 无硬编码密钥；选择器写入本项目选择器库  
- 结构可用 POM 或 fixture，见 `references/page-object-model.md`；框架级新设计仍先 Cursor 审核  

## 输出

短句中文，先结论：改了哪些定位/等待/断言、是否已落脚本、跑次结果与证据路径、未测项。不编造未跑结果。

## 来源

上游全文：`~/.agents/skills/playwright-best-practices/`（currents-dev，含 core / debugging / testing-patterns 等）。本目录 `references/` 为常用篇符号链接，按需 Read，勿整包塞进上下文。
