# 接手说明

另一套 Grok Bot 拉下本仓库后，按本文件接手。先看结论，再按步骤做。

新 Grok Bot 接手时读 `grokbot/MEMORY-EXPORT.md`。里面是已存储的指令、身份、职业、项目和偏好。

## 仓库放什么

本仓库放这些：

- 角色说明：`grokbot/bots/`。在用角色以 `grokbot/bots/roster.md` 为准。
- 共用技能备份：`grokbot/skills/`。
- 自动化框架：用例、页面、配置和执行入口。写法见根目录 `AGENTS.md`。
- 协作规范：本文件、`grokbot/README.md`、`grokbot/skills/project-bot-collab/`。
- 工作台映射正本：`grokbot/workbench-map.md`。常驻行、需求分析行和派单记录都在这里。

业务知识在各项目 Notion。业务知识不在 Git。

## 不放什么

下面这些不进 Git，也不写进技能正文或映射正本：

- 凭证
- 密码、token、密钥
- 测号密码
- 谷歌表链接
- 记忆
- 连接器登录态

工作台的对话地址和对话 id 可以进 Git，只写在 `grokbot/workbench-map.md`。2026-11-12 用户原话：「谁说不能进的，git那保存这些又没关系」。此前写过对话地址、对话 id 不进 Git，以这句为准。

## 新 Bot 接手步骤

1. 克隆本仓库。
2. 按 `grokbot/skills/` 导入共用技能。`grokbot/skills/project-bot-collab/CURSOR-WORKBENCH.md` 是工作台规范，用来补现网技能，不用它覆盖现网 `SKILL.md`。映射正本读 `grokbot/workbench-map.md`。
3. 按 `grokbot/bots/roster.md` 建角色。`bots/` 里早期四份模板保留作对照。实际项目机器人以花名册为准。
4. 在云电脑运行 `tools/bootstrap_bot_computer.sh`，重建工具链。
5. 重新授权 Notion、Google、GitHub 等连接器。连接器登录态不会随仓库过来。
6. 测试账号不在仓库。只到下面这些位置取，不要把内容抄进 Git：
   - 云电脑：`/workspace/qa/secrets/qa-test-accounts.md`
   - Windows 本地同名文件
   - Notion「测试账号」页
   - 保险库同名登录

## Cursor 两条通道

工作台给思考、方案、代码草稿。默认模型是 Grok 4.7。常驻是每个在用项目号一条对话。需求分析是一条需求一条对话。同类活续聊。不提前建满。

升级走常驻 Ask、Plan、Debug、Multitask，再加上 `tools/ask_cursor.py`。一事一案，一个 Agent，一个 PR。工作台不替代升级。

映射正本在 `grokbot/workbench-map.md`。对话地址和对话 id 写在这份正本里。打开映射先读这个文件。Google Drive 不再是打开映射的前提。交付文件仍可以用 Google Drive。

细则见 `grokbot/skills/project-bot-collab/CURSOR-WORKBENCH.md`。填空步骤见 `grokbot/skills/workbench-fill/SKILL.md`。共享框架要改代码并开 PR 时，走 `grokbot/bots/0-技能-Cursor专家升级.md`。

## nova

nova 项目暂停。先不建工作台。不派活。

## 怎么回答用户

给用户的回答要精简。先说结论。

把 Cursor 结果转给用户时，同样要短。

机器人自己核验 Cursor 结果。不把草稿当测过。不合并 PR。汇报不含凭证。

## 测试执行

点页面、跑脚本、取证、写测试报告，仍由机器人自己做。
