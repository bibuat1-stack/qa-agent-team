---
name: Cursor专家升级
description: >-
  团队自己解决不了的自动化问题时使用：整理脱敏证据，经 ask_cursor 闸门后交给 Cursor Cloud Agent（指定更强模型）做 advise
  或 fix，拿回结论后自行验证并记录账本。含常驻 Ask/Plan/Debug/Multitask 入口与一问题一案例规则。
---
# Cursor专家升级与常驻支援

用途：团队自己解决不了的问题，交给 Cursor Cloud Agent（指定更强的模型）诊断或修复，拿回结论后由我们自己验证并继续工作。也用于技术支持、框架方案、并行编排；结论留痕便于以后同类问题快速复用。一律在仓库 https://github.com/bibuat1-stack/qa-agent-team 下开或续聊 Cloud Agent，不要用 No Repo。

## 常驻对话（优先续聊，勿重复新建同类）

| 模式 | 用途 | Agent |
|------|------|-------|
| Ask | 只问答不改仓 | https://cursor.com/agents/bc-1ed350d6-a9d6-5553-9b91-8ae2e9b564ae |
| Plan | 框架/接入方案 | https://cursor.com/agents/bc-434058a7-1ab8-5168-85a2-3b829f639b93 |
| Debug | 根因诊断 | https://cursor.com/agents/bc-97dcceab-76f6-561b-ab07-361f1783c50c |
| Multitask | 多线编排建议 | https://cursor.com/agents/bc-a658069b-a92c-5574-854a-02e7d8bcc217 |

总控可自行开 Agent，模式按问题灵活选。同一失败特征仍走 `ask_cursor`：先 `status`，有案例就 `followup`，没有才 `prepare`。一问题一案例一 Agent 一 PR。

## 何时使用（满足任一条）
1. 同一测试以同样错误失败，已经自己尝试修复 2 次。
2. 失败类型未知：不是断言不符、测试数据、环境故障、超时或已知 flaky。
3. 修复需要改共享框架代码（conftest.py、common/、config/、fixtures、HTTP 客户端封装、Page Object、CI 配置）。只有这种情况用 fix 模式。
4. 需求有歧义，测试点取决于答案。用 advise 模式或 Ask 对话，列出你看到的几种理解。
5. 你对自己结论的置信度低于 0.6。

## 不要使用
- 服务或环境整体故障（所有接口 5xx、DNS 错误、测试账号过期）：直接报告给我。
- 重跑一次就通过的用例：标记为 flaky，记录证据。
- 今天已经升级过的同一问题，或已有进行中案例：只读账本结论或 followup，不能再发。

## 步骤
1. 整理证据（最多 8 份，每份存成文件）：完整的 pytest/Playwright 命令和退出码；堆栈；最后 200 行日志；失败用例的 Allure 结果（status、statusDetails）；接口失败时的请求和响应；你两次尝试的 diff；分支和 commit。
2. 去敏：不得包含令牌、密码、Cookie、Authorization 头，全部替换为 ***。脚本会再脱敏一次，但你必须先自己检查。
3. 运行闸门（在 /workspace/qa/repo 下）：
   python3 tools/ask_cursor.py prepare --mode advise --problem-file problem.md --context-file context.md --evidence log.txt --evidence allure.json --repo https://github.com/bibuat1-stack/qa-agent-team --ref <分支> --model <强模型ID>
   - decision=duplicate：不再升级，使用账本里的结论或继续等待中的结果。
   - decision=budget_exhausted：停止，走「人工兜底」。
   - decision=allowed：记下 hash，继续下一步。
4. 委派：把 brief.md 的全文交给对应模式的常驻 Agent（或该案例已有的 Agent），并明确写「使用模型 <强模型ID>」。advise 模式要求它只分析，不改文件、不推送；fix 模式要求它在新分支修复并打开 Pull Request。
5. 等 Cloud Agent 卡片显示 Done、Error 或 Expired。读取最终报告末尾的 json（diagnosis、solution、confidence）和 PR 链接。
6. 记录结果：
   python3 tools/ask_cursor.py record --hash <hash> --status answered --agent-url <Cloud Agent 链接> --pr-url <PR 链接> --confidence <0~1> --summary "<一句话结论>"
   Cloud Agent 根本没有启动时，加 --refund 退回额度。验证通过后 record --status verified，失败则 followup。

## 如何使用答复
- 在分支上应用方案（fix 模式直接使用它开的 PR），重跑失败用例和所在模块的用例，全部通过才算解决。
- confidence 低于 0.6：只当作假设，先做一次定向验证，再改代码。
- 对 PR：确认 diff 只改了预期文件，等 CI 通过，把链接写进报告。不要自己合并。
- 汇报时写你验证过的事实，不照抄专家的说法，并附上 Cloud Agent 链接。

## 与 Bot 协调
- 总控分派，每阶段一个负责人。
- 业务上下文在各项目 Notion；本仓放技能与案例留痕。
- 执行方先自查本项目知识库与自动化踩坑知识库，仍卡再升级；故障仍报总控。
- 不合并 PR；汇报不含凭据。

## 人工兜底
升级失败、额度用尽、或者方案验证不通过时：停止，不再重复升级。在 GitHub 仓库开一个 issue，附上证据、brief.md 和 Cloud Agent 链接，并提醒我在 Cloud Agent 卡片上点「Open in Cursor」接手。
