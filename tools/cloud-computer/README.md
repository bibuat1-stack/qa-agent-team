# 云电脑共用脚本备份

这里是云电脑 `/workspace/qa/` 上共用脚本的仓库副本。方案正文、登录态、租约样本、测号、密钥、表链接和对话链接都不放进本仓库。

云电脑上的运行位置：

| 仓库里的文件 | 拷到 |
| --- | --- |
| `qa-ready.sh` | `/workspace/qa/qa-ready.sh` |
| `bin/box_health.py` | `/workspace/qa/bin/box_health.py` |
| `bin/html_report.py` | `/workspace/qa/bin/html_report.py` |

拷贝示例（在仓库根目录执行，不跑 apt，也不调用 `bootstrap_bot_computer.sh`）：

```bash
mkdir -p /workspace/qa/bin
install -m 0755 tools/cloud-computer/qa-ready.sh /workspace/qa/qa-ready.sh
install -m 0755 tools/cloud-computer/bin/box_health.py /workspace/qa/bin/box_health.py
install -m 0755 tools/cloud-computer/bin/html_report.py /workspace/qa/bin/html_report.py
```

`qa-ready.sh` 缺 pytest 才安装仓库依赖，缺 Chromium 只执行 `playwright install chromium`（不加 `--with-deps`）。另外检查 pyotp、playwright-cli 和 agent-browser；后两个装到 `~/.local`，不需要 root。`/workspace/qa/bin` 会放进当前进程的 PATH，并在 `~/.bashrc` 里留一行。安装失败只把最后 30 行写入 `/workspace/qa/runs/bootstrap-error.log`，然后继续。

默认不跑体检。`--health` 才运行 `box_health.py`，`--clean` 才带清理；体检失败不改变 `qa-ready.sh` 的退出码。

`box_health.py` 的提示门槛是 2048 MiB。低于门槛时只在摘要里提示总控，退出码仍是 0，不拦截开工、开浏览器或收尾。每次把 SwapFree 写进摘要和 `health.jsonl`。`--clean` 只删除过期租约文件和没有进程引用的临时浏览器配置，不结束任何进程。

`html_report.py` 读当前目录的 `results.jsonl`，把自带原图的 `report.html` 写到同目录。图片用 data URI 嵌进文件；提供 `box` 时在图上画红框，白话写在图旁。不要把 `secrets` 或 `leases` 里的文件交给它。

本地核对（不进 CI 的用例收集）：

```bash
python3 tools/cloud-computer/check_backup.py
```
