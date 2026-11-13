# 接手说明

另一套 Grok Bot 拉下本仓库后，按本文件接手。先看结论，再按步骤做。

新 Grok Bot 接手时读 `grokbot/MEMORY-EXPORT.md`。里面是已存储的指令、身份、职业、项目和偏好。

## 仓库放什么

本仓库放这些：

- 角色说明：`grokbot/bots/`。在用角色以 `grokbot/bots/roster.md` 为准。
- 共用技能备份：`grokbot/skills/`。
- 自动化框架：用例、页面、配置和执行入口。写法见根目录 `AGENTS.md`。
- 协作规范：本文件、`grokbot/README.md`、`grokbot/skills/project-bot-collab/`。
- 工作台映射正本：`grokbot/workbench-map.md`。按 Grok Bot 账号分页：`工作台-Faker`、`派单记录-Faker`、`工作台-sacks`、`派单记录-sacks`，另有账号对照。现在查、写用 `工作台-Faker`。
- 备份分工：`grokbot/BACKUP.md`。Git 与 Google Drive「QA机器人备份」各放什么。

云电脑共用脚本的备份在 `tools/cloud-computer/`（`qa-ready.sh`、`bin/box_health.py`、`bin/html_report.py`）。云电脑上仍运行 `/workspace/qa/qa-ready.sh` 和 `/workspace/qa/bin/` 里的同名文件。方案正文不进 Git。登录态、租约和测号也不进 Git。

业务知识在各项目 Notion。业务知识不在 Git。

## 不放什么

下面这些不进 Git，也不写进技能正文或映射正本：

- 凭证
- 密码、token、密钥
- 测号密码
- 凭证表链接
- 记忆正文
- Drive 备份包和 nova 备份
- 连接器登录态

工作台的对话地址和对话 id 可以进 Git，只写在 `grokbot/workbench-map.md`。2026-11-12 用户原话：「谁说不能进的，git那保存这些又没关系」。此前写过对话地址、对话 id 不进 Git，以这句为准。

## 测试账号在哪

密码不在这个仓库。仓库是公开的，所以密码、谷歌验证器密钥、token、webhook、表格链接、Notion 页面链接、文档 id 都不写进来。要用链接，打开本地文件，链接写在文件里。

五个位置：

1. 云电脑文件：`/workspace/qa/secrets/qa-test-accounts.md`
2. Windows 文件：`C:\Users\青鸟\Documents\qa-test-accounts.md`
3. Notion 页面，标题「测试账号」
4. 保险库登录项，名称与本地文件里的名称相同
5. Google 表格，标题「各项目测试账号与凭证」。一个项目一张工作表。表里把环境和系统分开标。不要把几个项目写进同一张工作表。

日常按快慢找，不按哪份算正式来源排：

- 先看云电脑文件 `/workspace/qa/secrets/qa-test-accounts.md`。这份最快。
- Windows 文件 `C:\Users\青鸟\Documents\qa-test-accounts.md` 是用户自己电脑上的本地副本。
- Google 表格「各项目测试账号与凭证」和 Notion 页「测试账号」是云端备份，用来防丢。日常不要先翻这两处。
- 保险库同名登录用来填登录表单，不拿来当第一查找处。

有人要看密码时，只指出 Notion「测试账号」页、上面的本地文件路径，或这张 Google 表格。密码和验证器密钥不贴进聊天、Git、记忆、通知，也不写进各项目知识库。

记 M3 域名 `j1-m3-web.newopsname.com` 时，环境标签写「测试」，不要写成 j1。

几份要对齐时，只补缺，不覆盖、不删除已有账号：

- 某一份少了账号，或用户名、密码、谷歌验证器密钥是空的，另一份已经填好：保留已填的值，把缺的补上。
- 不要用空的本地文件或空行，盖掉云端里已经有的账号。
- 不要用云端的空行，清掉本地已经有的账号。
- 口诀：空的不覆盖有内容的；缺的行追加；已经填好的值不清空。

## 新 Bot 接手步骤

1. 克隆本仓库。
2. 按 `grokbot/skills/` 导入共用技能。`grokbot/skills/project-bot-collab/CURSOR-WORKBENCH.md` 是工作台规范，用来补现网技能，不用它覆盖现网 `SKILL.md`。映射正本读 `grokbot/workbench-map.md`。
3. 按 `grokbot/bots/roster.md` 建角色。`bots/` 里早期四份模板保留作对照。实际项目机器人以花名册为准。
4. 在云电脑第一次重建工具链时运行 `tools/bootstrap_bot_computer.sh`。日常开工不要跑它，也不要跑 apt；运行 `/workspace/qa/qa-ready.sh`。这份脚本的仓库备份在 `tools/cloud-computer/qa-ready.sh`，体检和批次 HTML 报告的备份在同目录 `bin/`。体检低于 2048 MiB 时只提示，退出码仍是 0。
5. 重新授权 Notion、Google、GitHub 等连接器。连接器登录态不会随仓库过来。
6. 测试账号不在仓库。去哪找、先看哪一份、怎么同步，见本文件「测试账号在哪」。不要把密码抄进 Git。

## Cursor 两条通道

工作台给思考、方案、代码草稿。默认模型是 Grok 4.7。常驻是每个在用项目号一条对话。需求分析是一条需求一条对话。同类活续聊。不提前建满。

升级走常驻 Ask、Plan、Debug、Multitask，再加上 `tools/ask_cursor.py`。一事一案，一个 Agent，一个 PR。工作台不替代升级。

映射正本在 `grokbot/workbench-map.md`。谷歌表「QA机器人Cursor工作台」只是同步副本，页也按账号分开。谷歌硬盘只保存全量压缩包。日常先把映射同步到 Git，再把压缩包备份到硬盘。查表先打开对应账号那一页。现在在用的是 `工作台-Faker` 和 `派单记录-Faker`。`工作台-sacks` 只作历史对照，不得续聊，那些稳定 id 不要当成当前号。工作台-Faker 里，自动化踩坑知识库常驻已是「在用」。其余 Faker 行的对话列仍为空。

细则见 `grokbot/skills/project-bot-collab/CURSOR-WORKBENCH.md`。填空步骤见 `grokbot/skills/workbench-fill/SKILL.md`。共享框架要改代码并开 PR 时，走 `grokbot/bots/0-技能-Cursor专家升级.md`。

## nova

nova 项目暂停。先不建工作台。不派活。

## 怎么回答用户

给用户的回答要精简。先说结论。

把 Cursor 结果转给用户时，同样要短。

机器人自己核验 Cursor 结果。不把草稿当测过。不合并 PR。汇报不含凭证。

## 测试执行

点页面、跑脚本、取证、写测试报告，仍由机器人自己做。
