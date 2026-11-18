# 云电脑浏览器怎么开

UI 回归默认无头、直连，不走 `127.0.0.1:8791`，也不开平台桌面 Chrome。平台那只浏览器的策略、启动参数和代理都不要改。

有头窗口和固定视口默认 **1920×1200**。页面简单或要省资源时，再传入更小的宽高。时区 `Asia/Shanghai`，语言 `zh-CN`。有头直连窗口的配置目录是 `~/.config/chrome-direct`（可用环境变量 `QA_CHROME_DIRECT_PROFILE` 换路径），和平台 Chrome 分开。

慢主要在平台桌面 Chrome 被强制走 8791，不在渲染。软件渲染按像素耗 CPU，影响不大时就用默认大窗口。

## 怎么选

- 回归：无头 Playwright。用 `launch_kwargs()`（默认无头）和 `context_kwargs()`（默认 1920×1200）。不要开窗口，也不要复用 `chrome-direct` 配置目录。
- 只要看页面：用 Playwright 页面截图，无头即可。
- 人要盯着看或接手：`open_direct_headed.py`。它只开直连有头窗口。
- 只有直连已经证实不通、必须用保险库填表、或用户明确要平台那只浏览器时，才走平台桌面 Chrome。开工前先提醒用户。

## 启动示例

回归写在调用方里，不要为了回归去跑下面的有头脚本：

```python
from browser_defaults import context_kwargs, launch_kwargs

browser = chromium.launch(**launch_kwargs())
context = browser.new_context(**context_kwargs())
# 页面简单或要省资源时才改小，只传一边时另一边仍是 1920 或 1200：
# context = browser.new_context(**context_kwargs(width=1280, height=800))
```

有头窗口（用完自己关，不要结束别人的浏览器进程）：

```bash
QA_OWNER=号名 DISPLAY=:1 python3 /workspace/qa/bin/open_direct_headed.py https://example.com
QA_OWNER=号名 DISPLAY=:1 python3 /workspace/qa/bin/open_direct_headed.py --once https://example.com
QA_OWNER=号名 DISPLAY=:1 python3 /workspace/qa/bin/open_direct_headed.py --width 1280 --height 800 https://example.com
```

`--once` 打开到 load 就关，用来核对启动参数。没有 `DISPLAY` 时直接退出，退出码 2，不会去开平台 Chrome。宽或高不是正整数时也是退出码 2。

## 调用约定

这些函数的参数和以前一样：

- `launch_kwargs(headless=True, width=None, height=None)`：给 `chromium.launch`。默认无头，`proxy` 固定是 `None`。
- `context_kwargs(width=None, height=None)`：给 `browser.new_context`。每次返回新字典。
- `persistent_context_kwargs(headless=False, width=None, height=None)`：给 `chromium.launch_persistent_context`。默认有头，并用 `~/.config/chrome-direct`。
- `viewport_for(width=None, height=None)`、`launch_args(width=None, height=None)`：要改窗口时传参。`launch_args()` 默认结果与 `LAUNCH_ARGS` 相同，但是一份新列表。
- `command_uses_proxy(args)`：只有 `--proxy-server` 或 `--proxy-pac-url` 才算走代理。`--no-proxy-server` 是直连。不要再用「参数字符串里有没有 proxy」来判断，那会把直连误判成代理。

改窗口大小传 `width`、`height`，或命令行的 `--width`、`--height`。不要写 `args[0] = "--window-size=..."`。`LAUNCH_ARGS` 里的窗口尺寸只是默认值，按下标改它会在别人调整参数顺序后悄悄改错项。

`0` 不会再被当成「没传」。不传就是 1920×1200；传了就必须是正整数。

## 换到云电脑前先对照

现网跑的是 `/workspace/qa/bin/` 里的同名文件。这份是仓库备份，合并后不会自动盖掉现网。在仓库根目录对照：

```bash
diff -u /workspace/qa/bin/browser_defaults.py tools/cloud-computer/bin/browser_defaults.py
diff -u /workspace/qa/bin/open_direct_headed.py tools/cloud-computer/bin/open_direct_headed.py
diff -u /workspace/qa/bin/README-browser.md tools/cloud-computer/bin/README-browser.md
```

不要把密码、测号或代理口令写进这三份文件、浏览器配置或命令行。登录态和账号租约不在这里，登录仍按现有约定，先查租约再登。
