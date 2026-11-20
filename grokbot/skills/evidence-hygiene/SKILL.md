---
name: evidence-hygiene
description: >-
  截图、HAR、录屏、日志要外发或写入报告前使用。脱敏 Cookie、Authorization 与他人 PII。测号密码不再一律脱敏。保留对排查有用的 trace id
  与请求形状。密钥类仍不外写。
---
# 证据脱敏（机器人优化版）

截图、HAR、录屏、终端摘录外发或写入 Notion、聊天前，用本技能处理密钥类和他人 PII。测试账密可以留在报告、聊天、Notion 和记忆里。本技能不扩大授权。密钥类仍禁止复制、删除、重置、改值。

## 原则

证据是为了让人能信与能跟。多出来的活 Cookie、真用户 PII、无用内部细节不要带出去。

## 两类敏感

1. **密钥类**：会话 Cookie、OAuth/refresh、API key、Authorization → 一律脱敏。测号密码不在此列
2. **他人 PII**：真名、邮箱、手机、地址、人脸 → 默认打码。演示跨账号影响时也尽量最小化

可保留：trace id、request id、时间戳、测试账号和密码、接口路径与响应形状、非会话类分析 Cookie

## 截图前检查

- Network Headers / Application Cookies 面板不在画面内
- 地址栏无 token 查询串
- 终端无 `Copy as cURL` 带 Cookie 的整段
- 拍完全分辨率再搜 Cookie 名与值前缀，有则打黑条

## HAR / 文本

对 Cookie、Set-Cookie、Authorization 做替换为 `<REDACTED>` 后再附件。不要整份未 scrub 的 HAR 丢进聊天。

## 与项目约定

- 对外通知、Notion、记忆：可以写测试账密。仍禁止密钥类密文、验证码、token、Cookie、API key、Authorization
- 本地留痕可按方便记，但外发前必须过本技能
- 资金类截图额外检查金额与真实用户标识

## 输出

确认已脱敏的文件路径列表。未 scrub 的标「不可外发」。
