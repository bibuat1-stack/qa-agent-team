# 云电脑浏览器怎么开

慢主要在平台桌面 Chrome 被强制走 8791 代理，不在渲染。平台那只浏览器的策略和代理不要改。

默认路线：

- 接口和可重复回归：无头 Playwright，直连，不要开平台 Chrome。
- UI 回归无论无头还是有头，默认用 1920×1200 大视口（有头窗口同样 1920×1200），减少动画，方便看清页面。影响不大时就用大窗口；页面简单或要省资源时，再传入更小的 `width`、`height`。
- 只要看页面：用 Playwright 页面截图，无头即可。
- 用户要盯着看或接手：用 `open_direct_headed.py` 开直连有头窗口，配置目录固定在 `~/.config/chrome-direct`，和平台 Chrome 分开。
- 只有直连不通、必须用保险库填表、或用户明确要平台那只浏览器时，才走平台桌面 Chrome。开工前先提醒用户。

共用参数在 `browser_defaults.py`：回归用 `launch_kwargs()`（默认无头）和 `context_kwargs()`；要改小时传入 `width`、`height`。

启动有头窗口示例：

```bash
QA_OWNER=T8T测试执行 DISPLAY=:1 python3 /workspace/qa/bin/open_direct_headed.py https://example.com
```

用完自己关。不要结束别人的浏览器进程。不要把密码写进浏览器配置。登录态文件和账号租约还没落地，登录仍按现有约定，先查租约再登。
