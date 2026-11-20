# grokbot

给 Grok Bot / Cursor Cloud Agent 用的角色设定、共用技能备份与约定说明。

新 Bot 接手先读 [`HANDOFF.md`](HANDOFF.md)。在用角色以 [`bots/roster.md`](bots/roster.md) 为准。

## 分工（2026-11-10）

| 存哪儿 | 放什么 |
|--------|--------|
| **Notion（各项目知识库）** | 业务上下文、记忆点、知识点、缺陷、进度。机器人开工主读这里。 |
| **本仓库 GitHub** | 角色设定、共用技能副本、稳定协作规范、工作台映射正本（`workbench-map.md`，含对话地址和对话 id）。可版本恢复，给 Cloud Agent 与新 Bot 读。 |
| **Google Drive「QA机器人备份」** | 按账号子目录保存周备份压缩包（记忆、花名册快照、例程、恢复说明、备份那一刻的工作点交接）。 |

测试账密两边都可以写，本仓库可以放测试账密明文。去哪找、怎么同步，见 [`HANDOFF.md`](HANDOFF.md) 的「测试账号在哪」。token、Cookie、密钥类仍不写。表链接和页面链接仍不放进本仓库。

## 目录

- `HANDOFF.md`：接手说明。仓库放什么、不放什么、测试账号去哪找、云电脑日常开工跑 `qa-ready.sh`、两条 Cursor 通道、nova 暂停、可复制转发文本、专项测试号。用户说「同步」的固定顺序与恢复验收见 `BACKUP.md`，本文件不另抄一套。
- `BACKUP.md`：Git 与 Google Drive 备份怎么分。日常先把共用内容同步到 Git；Drive 文件夹「QA机器人备份」只按账号子目录保存周备份压缩包。完整备份包根目录要有备份那一刻的工作点交接。恢复与同步的检查清单也在这份说明里。当前账号核对自己每个机器人应有的工作台，核实缺失的补上并读回。来源账号的最新完整包、较新的增量或 skill-sync 包，以及来源账号的工作台页，用来对照。方向不写死。Git 拉完不算同步完成。
- `skills/account-backup/`：本账号 Google Drive 周备份或换号全量备份。按 `BACKUP.md` 打包，包内必含这份交接。和日备读回不是同一件事。
- `workbench-map.md`：工作台映射。按账号分页，页名是`工作台-<账号名>`和`派单记录-<账号名>`。文件里已有的账号名只是例子。查、写进当前账号自己的页。本文件与 `BACKUP.md` 对正本在 Git 还是在表的说法不一致，恢复时不自动改认。
- `MEMORY-EXPORT.md`：新 Grok Bot 接手时读这份备份，里面是已存储的指令、身份、职业、项目和偏好。
- `bots/roster.md`：在用与暂停角色。实际项目机器人已经不是早期四个模板角色。
- `bots/`：早期四份模板保留，只作对照，不删除。另有 Cursor专家升级技能原文。
- `skills/`：Grok 共用技能的脱敏备份（`SKILL.md`）。以机器人侧 UpdateSkill 为准时，这里做可恢复副本。工作台规范在 `skills/project-bot-collab/CURSOR-WORKBENCH.md`，填空步骤在 `skills/workbench-fill/SKILL.md`。不拿旧协作 `SKILL.md` 覆盖现网技能。
- 不设 `memory/` 流水库：项目记忆点继续写 Notion。

## 使用

1. 接手：按 `HANDOFF.md` 克隆、导技能、按花名册建角色，并重新授权连接器。
2. 业务任务：先查本项目 Notion 知识库。
3. 写/改自动化：遵守仓库根 `AGENTS.md` 与 `.cursor/skills/`。
4. 思考、方案、代码草稿：走该机器人自己的工作台对话。查、写打开`工作台-<当前账号>`。文件里已有的账号名只是例子。谷歌表和 `workbench-map.md` 谁是正本，见 [`BACKUP.md`](BACKUP.md)，这里不另改认。谷歌硬盘只保存全量压缩包；日常先同步到 Git，再备份压缩包到硬盘。
5. 共享框架要开 PR：在 **qa-agent-team** 仓库下开 Cloud Agent（不要 No Repo），走 `tools/ask_cursor.py`。工作台不替代这条升级。
6. 同步技能：改完 Grok 技能后，把对应 `SKILL.md` 更新进本目录并开 PR。技能备份 PR 仍按仓库原规则：只含 `grokbot/skills/`，以及为这次备份同步的本 README 或 `AGENTS.md` 里对应说明时，CI 通过后由 Cloud Agent 自行合并进 main。含 `HANDOFF.md`、花名册或其他目录的规范包，请用户手动合并。

## 项目隔离

GO / nova / T8T / M3 等知识与授权严格隔离。本目录放跨项目共用的技能与红线。测试账密可以明文写入。密钥类仍不写。
