把 QA 机器人体系备份到用户自己的 Google Drive，目标是就算用户换了 bot 账号，也能照着备份马上恢复。依据是用户 2026-11-10 的原话：「备份到谷歌硬盘的东西可以丰富点，就是比如就算我换bot账号了也能马上用……一周一次大备份，每天一次小备份，具体备份哪些东西你看着来」，以及「用例表有必要？这种notion上不会丢」。Notion 里已经有的内容（知识库、用例、需求）不进备份包。规则以协作技能 {{skill:项目机器人协作与故障闭环}}「记忆点与每日备份」第 8 条为准。

每晚跑一次。周日这次做大备份，其余 6 天做小备份。

一、小备份（每天）
1. 全部用户技能：/home/box/agent-data/workflows/ 下每个技能文件夹整份打包。
2. 记忆：把总控能读到的自己的 profile、journal，以及共享 profile、共享 journal，按类型导出成 Markdown，每条带日期和来源。
3. 机器人花名册：/home/box/agent-data/agents/ 下每个机器人的 profile.json 和 settings.json，整理成「机器人清单.md」（id、名字、标题、一句职责），原 json 一起放进去。不碰 store.db、attachments、assets、voice-calls、*.secret。
4. 例程：总控自己所有例程的名字、时间和提示词原文导出成 Markdown。
5. RESTORE.md：换新账号后的恢复顺序。先装技能，再建机器人，然后贴回记忆，重建例程，重连 Notion、Google Drive、GitHub 等连接器，最后跑 qa-ready.sh。附各项目知识库入口和测试账号存放位置（只写位置）。

二、大备份（周日）另加：
6. /workspace/qa/qa-ready.sh 和 /workspace/qa/tools/ 下的脚本；qa-agent-team 仓库只记地址和分支。
7. /workspace/qa/snapshots/ 最近 30 天改动备份。
8. 各机器人 attachments 里的文档（单个不超过 20MB）。整包超过 300MB 先去掉第 8 项最大文件，并在 RESTORE.md 写明。

三、去密：打包前扫密码、token、验证码、TOTP、谷歌密钥、Cookie、.env 值和测试账号明文，命中整行删或换成「见本地配置」。/workspace/qa/secrets/、box-secrets.json、host-secrets.json、chrome-cookie-*.json、*.secret、.env 一律不打包。拿不准宁可删。

四、上传与清理：先确认 Drive 连接器可用，需要授权就停（第一次报一次，连续两次失败暂停例程）。文件名 qa-backup-daily-<YYYYMMDD>.zip / qa-backup-weekly-<YYYYMMDD>.zip，传到「QA机器人备份」文件夹，不共享。上传后读回核对名和大小，成功后才删旧包（只留最新大、小各一份，旧格式 qa-memory-skills-*.zip 也删）。失败时旧备份不删。本机 /workspace/qa/backups/ 只留最近一次。

五、汇报：成功只记账不发消息。失败、读回不符、处理不掉的凭证、授权失效时在总控聊天说明哪一步失败、旧备份在不在、用户要做什么，不贴凭证。
