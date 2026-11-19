# grokbot/scripts

机器人和 Cursor 共用的可复用脚本正本。按项目分子目录：`t8t/`、`go/`、`m3/`、`common/`。

本机入口：`/workspace/qa/scripts/` 只指向本目录，不再另养可改正文。同步以 Git 为准。谷歌硬盘只做镜像。

密码、token、cookie、密钥不进本目录和脚本正文，从本机账号本或环境变量读。

文件名用小写加下划线，动词加对象。每个脚本开头写清：一句话用途、怎么跑、密钥从哪读。

## 目录

| 脚本 | 项目 | 用法 | 密钥从哪读 |
| --- | --- | --- | --- |
| `t8t/ceopay_decrypt_response.py` | T8T / CEOpay | `python3 grokbot/scripts/t8t/ceopay_decrypt_response.py '<加密返回 JSON>'`，或从标准输入传入 | 无密钥，走站点解密接口 |
| `m3/m3_j1_add_ip_whitelist.sh` | M3 | `bash grokbot/scripts/m3/m3_j1_add_ip_whitelist.sh <ip> [remark]` | 本机密钥文件（默认 `/workspace/qa/secrets/m3-j1-ip-whitelist.env`，或环境变量 `M3_J1_WHITELIST_ENV`）。脚本不打印明文。入库不等于恢复 M3 测试任务。 |

`go/` 和 `common/` 先留占位，有脚本再补表。
