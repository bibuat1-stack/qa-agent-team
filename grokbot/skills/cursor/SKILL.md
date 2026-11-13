---
name: Cursor专家升级
description: >-
  团队自己解决不了的自动化问题时使用。同一失败特征始终是一个案例：先 status，有案例就在同一张 Cloud Agent 卡片上 followup，没有才 prepare。
  脱敏证据交给 Cursor Cloud Agent 做 advise 或 fix。验证失败继续追问，不另开 Agent 或第二个 PR。
---
# Cursor专家升级

用途：团队自己解决不了的问题，交给 Cursor Cloud Agent（指定更强的模型）诊断或修复。同一个问题始终是同一个案例：同一个 hash、同一个 Cloud Agent 卡片、同一个 Pull Request。验证失败就在这张卡片上追问，不要另开。

每个会升级的机器人都启用本技能，并用 `--owner` 写上自己的名字。没有单独角色文件的机器人同样执行。

## 何时使用（满足任一条）

下列条目只用于升级。思考、方案、代码草稿先看「与工作台的分流」。

1. 同一测试以同样错误失败，已经自己尝试修复 2 次。
2. 失败类型未知：不是断言不符、测试数据、环境故障、超时或已知 flaky。
3. 修复需要改共享框架代码（conftest.py、common/、config/、fixtures、HTTP 客户端封装、Page Object、CI 配置）。只有这种情况用 fix 模式。
4. 需求有歧义，测试点取决于答案。方案先走该机器人的工作台。只有答案要求改共享框架并开 PR 时，才用本技能的 advise 或 fix。
5. 你对自己结论的置信度低于 0.6。

## 不要使用
- 服务或环境整体故障（所有接口 5xx、DNS 错误、测试账号过期）：直接报告给我。
- 重跑一次就通过的用例：标记为 flaky，记录证据。
- 同一问题已经有案例：不要再 prepare 一个新的 Cloud Agent。先 status，再在原案例上 followup。
- 思考、方案、代码草稿：走该机器人自己的工作台对话。见「与工作台的分流」。

## 没有单独角色文件的机器人
仓库里的四个角色文件只写核心职责。没有单独角色文件的机器人要升级时，同样用本技能：
- 每次 prepare 和 followup 都带 `--owner <你的机器人名字>`。
- 先运行 `python3 tools/ask_cursor.py status`。开放案例对得上（同一个失败用例节点、同一个 PR，或同一个问题）就 followup，不要 prepare。
- 只有 status 显示没有案例时才 prepare。
- 追问次数用尽：在 GitHub 开 issue，把 Cloud Agent 卡片交给人（Open in Cursor），不要再 followup。
- 没有人批准，不要改共享框架代码（conftest.py、common/、config/、Page Object、CI 配置）。
- 默认用 advise 模式。只有必须改本仓库代码时才用 fix，并带 `--repo`。

## 与工作台的分流

思考、方案、代码草稿走该机器人自己的工作台对话。不跑 `ask_cursor.py prepare`。不占升级每日额度。

只有要改共享框架并开 PR 时，才走本技能的 prepare / fix。

工作台不替代常驻 Ask、Plan、Debug、Multitask。不按机器人再复制这四个席位。

机器人与对话的映射正本在仓库 `grokbot/workbench-map.md`。查映射先打开对应账号那一页，现在在用的是「工作台-Faker」。对话地址和对话 id 写在该文件，可以进 Git。谷歌表只是同步副本。谷歌硬盘只保存全量压缩包；日常先同步到 Git，再备份压缩包到硬盘。本技能不抄具体对话地址，也不写密码、token、密钥、测号、凭证表链接。工作台正文见仓库 `grokbot/skills/project-bot-collab/CURSOR-WORKBENCH.md`。

## 步骤
1. 先找回案例（电脑重建后也要做）：
   python3 tools/ask_cursor.py status
   若知道 PR：python3 tools/ask_cursor.py status --pr-url <PR 链接>
   已有案例就跳到「追问」。没有才新建。
2. 整理证据（最多 8 份，每份存成文件）：完整的 pytest/Playwright 命令和退出码；堆栈；最后 200 行日志；失败用例的 Allure 结果（status、statusDetails）；接口失败时的请求和响应；你两次尝试的 diff；分支和 commit。证据里要带上 pytest 节点，例如 tests/api/example_posts/test_posts.py::TestPosts::test_get_post_detail。
3. 去敏：不得包含令牌、密码、Cookie、Authorization 头，全部替换为 ***。脚本会再脱敏一次，但你必须先自己检查。
4. 新建案例（在 /workspace/qa/repo 下）：
   python3 tools/ask_cursor.py prepare --mode advise --problem-file problem.md --context-file context.md --evidence log.txt --evidence allure.json --repo https://github.com/bibuat1-stack/qa-agent-team --ref <分支> --model <强模型ID> --owner <你的角色名>
   - decision=allowed：记下 hash。把 brief.md 全文交给一个新的 Cursor Cloud Agent，并写明「使用模型 <强模型ID>」。这是第 1 轮。
   - decision=continue：已经有结论。不要新开 Agent。按 next 去验证，或运行 followup。
   - decision=duplicate 且 status=pending：Agent 还在跑就等待；还没有发出去就把返回的已有 brief.md（第 1 轮）或 followup.md 再贴到原卡片。不要写第二份提示。
   - decision=duplicate 且 status=blocked，或 decision=followups_exhausted：停止，走「人工兜底」。
   - decision=budget_exhausted：停止，走「人工兜底」。
5. advise 模式只分析，不改文件、不推送。fix 模式第 1 轮在新分支修复并打开一个 Pull Request。追问仍用同一个模型和同一张卡片。
6. 等 Cloud Agent 卡片显示 Done、Error 或 Expired。读取最终报告末尾的 json（diagnosis、solution、confidence）和 PR 链接。
7. 记录结果：
   python3 tools/ask_cursor.py record --hash <hash> --status answered --agent-url <Cloud Agent 链接> --pr-url <PR 链接> --confidence <0~1> --summary "<一句话结论>"
   Cloud Agent 根本没有启动时，加 --refund 退回额度。案例保留为 pending，把原来的 brief.md 再发一次，不要删案例。
8. 验证：在分支上应用方案（fix 模式直接使用它开的 PR），重跑失败用例和所在模块的用例。
   - 全部通过：python3 tools/ask_cursor.py record --hash <hash> --status verified --pr-url <PR 链接> --summary "<验证通过>"
   - 没有通过：不要新开 Agent，进入「追问」。

## 追问（同一个案例）
python3 tools/ask_cursor.py followup --hash <hash> --why "<验证看到的现象，至少20字>" --evidence <新日志> --owner <你的角色名>
- 把 followup.md 全文粘贴进原来的 Cloud Agent 卡片。不要新开 Agent，不要新开第二个 PR。fix 模式继续已有分支和 PR；还没有 PR 时才打开一个。advise 模式仍然不改文件、不提交、不推送。
- 追问不占用每日新案例额度。每个案例默认最多 3 次（ASK_CURSOR_FOLLOWUPS）。
- decision=already_pending（退出码 3）：不要再写一份。next 让你等待就等；还没贴出去就把返回的 prompt_path 再贴一次。
- 结束后同样 record。再验证。通过就 record --status verified，失败就再 followup，直到次数用尽。
- 备用通道才用 api --send。对方还在跑时退出码 6，等待即可，不要把旧答复当成新结论。

## 如何使用答复
- confidence 低于 0.6：只当作假设，先做一次定向验证，再改代码。
- 对 PR：确认 diff 只改了预期文件，等 CI 通过，把链接写进报告。不要自己合并。
- 汇报时写你验证过的事实，不照抄专家的说法，并附上 Cloud Agent 链接。

## 人工兜底
追问次数用尽、额度用尽、或 Cloud Agent 起不来时：停止 followup。在 GitHub 仓库开一个 issue，附上证据、brief.md（或 followup.md）和 Cloud Agent 链接，并提醒我在 Cloud Agent 卡片上点「Open in Cursor」接手。只有我明确说可以重开时，才运行 followup --hash <hash> --reopen --why "..." --evidence <日志>。
