---
name: playwright-cli
description: 用 playwright-cli 做网页探路、抓无障碍快照、点控、录制、抓网络与控制台、生成定位器。网页探路默认用本技能。可重复回归仍以仓库脚本为准。
---
# playwright-cli

独立浏览器，不驱动平台桌面浏览器。选型以 box-ui-speed 为准，不要把本工具、浏览器连接和 agent-browser 写成并列可选。

## 会话

每次都带项目短名会话，避免和别的任务互相踩。

1. 打开目标地址。
2. 抓快照。大页先按文案查找节点，不整树硬扫。
3. 按快照里的引用点击或填写。导航后重新抓快照。
4. 看请求和控制台，区分前端和接口。
5. 结束时关闭该会话。

同一步失败两次就停，不连点。

## 留痕和落脚本

开批就打开路径留痕，截图和快照都开。收批停止，产物放本批目录。

跑通后生成定位器或停止录制，落成仓库里的 Playwright 脚本。定位用角色、可访问名或测试标识，不手抄易变样式，不猜像素。

登录态可以保存和加载，文件按项目隔离。密码和令牌不写进聊天，不写进会推到 GitHub 的文件。

有头、无头和 Playwright Extension 怎么选，见 box-ui-speed「有头、无头和 Playwright Extension」。

1. 边改脚本、不用盯画面：无头自己开浏览器。登录态用 `state-save` / `state-load`。
2. 接已经打开、已经登录的窗口：优先 `attach --cdp`，只接自己拉起的 Chrome for Testing。
3. 插件接已打开的有头窗口：`attach --extension`。配好自动连接 token 可自动连。token 不写进仓库、聊天或技能正文。
4. 无头不要走 `attach --extension`。登录态仍用 `state-save` / `state-load`，或对自己拉起的无头 Chrome for Testing 走 `attach --cdp`。

只在测试环境做请求拦截。生产配置禁止。生产上禁止提交的操作，这里也不做成会提交的步骤。
