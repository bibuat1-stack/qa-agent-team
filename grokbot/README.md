# grokbot

给 Grok Bot / Cursor Cloud Agent 用的角色设定、共用技能备份与约定说明。

## 分工（2026-11-10）

| 存哪儿 | 放什么 |
|--------|--------|
| **Notion（各项目知识库）** | 业务上下文、记忆点、知识点、缺陷、进度。机器人开工主读这里。 |
| **本仓库 GitHub** | 角色设定、共用技能副本、稳定协作规范。可版本恢复，给 Cloud Agent 与新 Bot 读。 |

凭证、token、Cookie、测号密码：**两边都不写**。

## 目录

- `bots/`：四个角色 + Cursor专家升级技能原文（粘贴/对照用）
- `skills/`：Grok 共用技能的脱敏备份（`SKILL.md`）。以机器人侧 UpdateSkill 为准时，这里做可恢复副本。
- 不设 `memory/` 流水库：项目记忆点继续写 Notion。

## 使用

1. 业务任务：先查本项目 Notion 知识库。
2. 写/改自动化：遵守仓库根 `AGENTS.md` 与 `.cursor/skills/`。
3. 遇技术卡点：在 **qa-agent-team** 仓库下开 Cloud Agent（不要 No Repo），走 `tools/ask_cursor.py`。
4. 同步技能：改完 Grok 技能后，把对应 `SKILL.md` 更新进本目录并开 PR。只含技能备份（可带本 README 或 `AGENTS.md` 里对应的一两句说明）时，CI 通过后由 Cloud Agent 自行合并进 main。

## 项目隔离

GO / nova / T8T / M3 等知识与授权严格隔离。本目录只放跨项目共用的技能与红线，不写具体业务账号与环境秘密。
