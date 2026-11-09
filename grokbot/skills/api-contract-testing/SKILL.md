---
name: api-contract-testing
description: >-
  核对 API 契约、OpenAPI/Collection 与实现是否一致，或做消费方契约回归时使用。优先本项目已有 Postman/OpenAPI 与
  api-testing 技能，预期必须有依据。
---
# API 契约测试（机器人优化版）

验证请求/响应形状、状态码与字段约定，防止破坏性变更。不扩大项目授权，不做生产资金写操作。

## 何时用

- 改接口前后要锁契约
- OpenAPI / Postman Collection 与实现要对齐
- 消费方担心提供方破坏兼容

## 工具优先级

1. 本环境已有：`api-testing`、`application-testing`、`collection-schema-v3`、`ci-integration`
2. Postman / OpenAPI 校验
3. 需要 Pact 等消费方契约时再引入，不强行新框架
4. UI 回归里的接口断言用 Playwright `APIRequestContext` 或监听摘要

## 做法

1. 找到本项目权威契约（OpenAPI、Collection、知识点里的字段表）
2. 对关键路径跑契约断言：必填字段、类型、枚举、错误码
3. 破坏性变更单独列出：删字段、改类型、收紧枚举、改状态码语义
4. 预期必须能指到契约或知识点。无依据标待确认

## 与 UI 联测

能 API 冒烟先 API。UI 只覆盖契约盖不住的呈现与状态机。选型见 [automation-regression](sand-workflow:automation-regression)。

## 输出

短句中文：通过/失败/未跑、契约来源、破坏点列表、证据路径。凭证不进报告正文。
