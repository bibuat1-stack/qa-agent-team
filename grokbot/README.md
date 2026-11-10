# grokbot

给 Grok Bot / Cursor Cloud Agent 用的角色设定、共用技能备份与约定说明。

## 分工（2026-11-10）

| 存哪儿 | 放什么 |
|--------|--------|
| **Notion（各项目知识库）** | 业务上下文、记忆点、知识点、缺陷、进度。机器人开工主读这里。 |
| **本仓库 GitHub** | 角色设定、共用技能副本、稳定协作规范。可版本恢复，给 Cloud Agent 与新 Bot 读。 |

凭证、token、Cookie、测号密码：**两边都不写**。

## 目录

- `bots/`：2026-11-10 现网花名册（32 个，文件名即稳定名）。早期四个角色草稿（`0-` 到 `4-`）仍留着，现网职责以花名册文件为准。模板只含名字、标题、描述，以及 settings 里的 `notify_on_agent_updates`。描述里的机器人 id、技能 id 写成 `{{bot:稳定名}}`、`{{skill:稳定名}}`。
- `skills/`：现网 51 个用户技能。`project-bot-collab` 是「项目机器人协作与故障闭环」v3.13。原来以数字 slug 命名的技能，目录改成稳定名。
- `routines/`：总控 4 条例程原文。其他机器人的例程待各机器人自报。
- `mapping/id-map.example.yaml`：名字到空账号槽的样子。真实 id 映射不进 Git，由导出脚本写到仓库外。
- 不设 `memory/` 流水库：项目记忆点继续写 Notion。

重新导出（在云电脑上，只读来源）：

```bash
python3 tools/export_grokbot_roster.py \
  --agents /home/box/agent-data/agents \
  --workflows /home/box/agent-data/workflows \
  --routines /path/to/routine-markdown \
  --dest /workspace/qa/repo/grokbot \
  --id-map /workspace/qa/private/id-map.yaml
```

`--id-map` 必须在 Git 工作区之外。例程原文若只在服务端、磁盘上没有目录，可以不传 `--routines`，脚本不会覆盖已入库的例程。

## 使用

1. 业务任务：先查本项目 Notion 知识库。
2. 写/改自动化：遵守仓库根 `AGENTS.md` 与 `.cursor/skills/`。
3. 遇技术卡点：在 **qa-agent-team** 仓库下开 Cloud Agent（不要 No Repo），走 `tools/ask_cursor.py`。
4. 同步技能：改完 Grok 技能后，把对应 `SKILL.md` 更新进本目录并开 PR。只含技能备份（可带本 README 或 `AGENTS.md` 里对应的一两句说明）时，CI 通过后由 Cloud Agent 自行合并进 main。

## 项目隔离

GO / nova / T8T / M3 等知识与授权严格隔离。本目录只放跨项目共用的技能与红线，不写具体业务账号与环境秘密。
