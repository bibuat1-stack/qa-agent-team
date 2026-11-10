# 总控（King, {{bot:King}}）例程原文，导出于 2026-11-10
其他机器人的例程由各机器人自己导出，本包未含。

## 新增项目机器人协作规范巡检
- schedule: CRON_TZ=Asia/Irkutsk 0 9 * * 1-5，flexible ±30
- prompt：见 king-coord-check.md

## 三项目知识库每日存档巡检
- schedule: CRON_TZ=Asia/Shanghai 30 23 * * *，flexible ±15
- prompt：见 king-kb-archive-check.md

## 云电脑闲置资源夜间清理
- schedule: CRON_TZ=Asia/Shanghai 45 22 * * *，flexible ±15
- prompt：见 king-idle-clean.md

## QA机器人 Google Drive 备份（每日小备份，周日大备份）
- schedule: CRON_TZ=Asia/Shanghai 55 23 * * *，flexible ±15
- prompt：见 king-drive-backup.md

其他机器人例程：待各机器人自报。
