---
name: box-ui-speed
description: 做浏览器探路、走查、填表或点按钮之前使用。网页默认 playwright-cli，可重复回归用仓库 Playwright 脚本。不把三种浏览器工具写成并列可选。
---
# 探路选型

少开桌面、少截图轮询、少猜坐标。不跨项目借账号。

## 默认路线

页面工作默认直连。不要改平台桌面浏览器的启动参数，也不要给独立浏览器套上平台桌面浏览器那条代理。

| 场景 | 用什么 |
| --- | --- |
| 接口断言、造数、查状态 | 接口，不点页面 |
| 可重复的 UI 回归 | 仓库 Playwright 脚本，无头，加载本项目登录态 |
| 网页探路和一次性走查 | playwright-cli。开批即留路径痕迹，收批停止。不混开两套工具抢同一测号 |
| 必须看画面 | Playwright 页面截图，无头即可。用户要实时看或接手时才开有头窗口，并先说明原因 |
| 只能用保险库填表，或登录要用户接管 | 平台桌面浏览器。开工前先说明原因，没说明不得开工 |
| 同一地址直连已经证实失败 | 才允许改走平台桌面浏览器，并写明原因 |

可重复路径禁止用桌面点屏当回归。独立浏览器不是平台桌面那扇窗，不要用脚本去驱动平台桌面浏览器窗口。

## 有头、无头和 Playwright Extension（2026-11-21 Asia/Shanghai 实测）

实测环境：云电脑上的 Google Chrome for Testing 158（配置目录 `~/.config/chrome-direct`），用 playwright-cli 对比无头自己开浏览器、有头调试端口直连、Playwright Extension 连接。测试页标题 CMP-EXT-20261121-1641。

1. 边测边改脚本、不用盯画面：用无头。脚本自己开浏览器，实测约 1 秒起来；登录再点操作一轮约 2.5 秒；改完再跑一条约 0.8 秒。不用点「允许连接」。登录态用 playwright-cli 的 state-save / state-load 复用，不必靠插件。
2. 要盯着看、边改边看页面：开有头 Chrome for Testing（配置目录 `~/.config/chrome-direct`，启动参数见云电脑 `/workspace/qa/bin/browser_defaults.py` 的 `persistent_context_kwargs`）。连上之后，改一条再跑的速度和无头同一量级（实测约 0.8–1.2 秒）。
3. 接已经打开、已经登录的有头窗口：优先用 Chrome for Testing 的调试端口直连（`playwright-cli attach --cdp`）。实测有头约 0.9 秒、无头约 0.6 秒，能直接看到当前页，不用点允许。只接我们自己拉起的 Chrome for Testing，禁止用 CDP / Playwright / xdotool 去接或驱动平台那只桌面 Chrome（通常调试端口 9224、强制走 8791 代理）。
4. Playwright Extension（Chrome Web Store id `mmlmfjhmonkocbjadbfplnigmagldckm`，官方解包副本在云电脑 `/workspace/qa/browser-extensions/playwright-extension`）也可接已打开的有头窗口。Chrome for Testing 不能从商店装扩展，有头直连窗口启动时加载这份官方副本；无头回归不加载。配好自动连接 token 后约 1 秒能连上；不配要在「Connect to Playwright」页点允许。自动连上后默认往往是空白页，登录态还在，但不会自动停在原来盯着的那一页，还要再打开对应地址。不要把 token 写进仓库、聊天或技能正文。
5. 无头不要走这个插件：扩展能加载，但 attach 连不上。没有可点的连接页，带上 token 等了 20 秒也没连上。无头复用登录态用 state-save / state-load，或对自己拉起的无头 Chrome for Testing 走调试端口直连。

## 优先级

1. 有接口就用接口。
2. 可重复回归只跑仓库脚本。下次只跑脚本。
3. 网页探路默认 playwright-cli。Playwright 的浏览器连接只用于不需要路径留痕的快速查看。agent-browser 只作备用。
4. 能复用的操作或测试用例都要写成复用脚本，脚本要边测边改。探路跑通后当场用定位器生成或录制停止，写成 Playwright 脚本。第二次起回到跑脚本。
5. 读不到按钮结构的画布、游戏画面、图表，改走 canvas-ui-testing。普通页先读结构树。
6. 网页工具都够不到的原生桌面，才用桌面操作。

登录态文件按项目隔离。明文密码不进聊天，不进会推到 GitHub 的文件。

踩坑写进共用踩坑库，字段按 ui-auto-coordinator：问题、改法、结果、仍未证明什么。本技能不替人排障到底，也不把探路交给别的机器人。
