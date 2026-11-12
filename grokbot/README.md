# grokbot

给 Grok Bot / Cursor Cloud Agent 用的角色设定、共用技能备份与约定说明。

新 Bot 接手先读 [`HANDOFF.md`](HANDOFF.md)。在用角色以 [`bots/roster.md`](bots/roster.md) 为准。

## 分工（2026-11-10）

| 存哪儿 | 放什么 |
|--------|--------|
| **Notion（各项目知识库）** | 业务上下文、记忆点、知识点、缺陷、进度。机器人开工主读这里。 |
| **本仓库 GitHub** | 角色设定、共用技能副本、稳定协作规范、工作台映射正本（`workbench-map.md`，含对话地址和对话 id）。可版本恢复，给 Cloud Agent 与新 Bot 读。 |

凭证、token、Cookie、测号密码：**两边都不写**。

## 目录

- `HANDOFF.md`：接手说明。仓库放什么、不放什么、两条 Cursor 通道、nova 暂停。
- `workbench-map.md`：工作台映射正本。常驻行、需求分析行、派单记录。对话地址和对话 id 写在这里。
- `MEMORY-EXPORT.md`：新 Grok Bot 接手时读这份备份，里面是已存储的指令、身份、职业、项目和偏好。
- `bots/roster.md`：在用与暂停角色。实际项目机器人已经不是早期四个模板角色。
- `bots/`：早期四份模板保留，只作对照，不删除。另有 Cursor专家升级技能原文。
- `skills/`：Grok 共用技能的脱敏备份（`SKILL.md`）。以机器人侧 UpdateSkill 为准时，这里做可恢复副本。工作台规范在 `skills/project-bot-collab/CURSOR-WORKBENCH.md`，填空步骤在 `skills/workbench-fill/SKILL.md`。不拿旧协作 `SKILL.md` 覆盖现网技能。
- 不设 `memory/` 流水库：项目记忆点继续写 Notion。

## 使用

1. 接手：按 `HANDOFF.md` 克隆、导技能、按花名册建角色，并重新授权连接器。
2. 业务任务：先查本项目 Notion 知识库。
3. 写/改自动化：遵守仓库根 `AGENTS.md` 与 `.cursor/skills/`。
4. 思考、方案、代码草稿：走该机器人自己的工作台对话。映射正本是 `workbench-map.md`。对话地址和对话 id 写在该文件。打开映射先读它。Google Drive 不再是打开映射的前提。交付文件仍可以用 Google Drive。
5. 共享框架要开 PR：在 **qa-agent-team** 仓库下开 Cloud Agent（不要 No Repo），走 `tools/ask_cursor.py`。工作台不替代这条升级。
6. 同步技能：改完 Grok 技能后，把对应 `SKILL.md` 更新进本目录并开 PR。技能备份 PR 仍按仓库原规则：只含 `grokbot/skills/`，以及为这次备份同步的本 README 或 `AGENTS.md` 里对应说明时，CI 通过后由 Cloud Agent 自行合并进 main。含 `HANDOFF.md`、花名册或其他目录的规范包，请用户手动合并。

## 项目隔离

GO / nova / T8T / M3 等知识与授权严格隔离。本目录只放跨项目共用的技能与红线，不写具体业务账号与环境秘密。
