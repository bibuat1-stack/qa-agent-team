---
name: ui-interaction-kit
description: 走查、UI自动化或读页面控件时使用。跨项目通用UI交互约定：优先无障碍树/DOM，像素兜底，统一按钮弹层表格状态判定，并可挂项目特有热区与样例。
---
# 通用 UI 交互资料包

跨项目共用模板。项目入口、测号、知识库、审批边界以该机器人职责与本项目知识库为准，本技能不扩大授权、不跨项目借账号或入口。

## 何时加载

- 走查、点按、填表、认弹层或读页面状态
- 写或改 UI 自动化定位与断言
- 要把通用交互约定喂进执行脚本或知识库
- 用户要求「先读懂页面再操作」

## 读页面优先级

1. 无障碍树 / 角色与可访问名（button、textbox、dialog、listbox、table）
2. 稳定 DOM：`data-testid`、语义角色、稳定 `id`/`name`（避开易变 class 与纯坐标）
3. 结构化状态：disabled、aria-busy、aria-expanded、hidden、loading
4. 像素 / 模板 / OCR 仅作兜底，且必须有「可点/不可点」对照样例
5. 有接口时并行挂监听，区分前端展示问题与接口问题，流量可落成后续 API 素材

取树工具：Playwright MCP `browser_snapshot`、[playwright-cli](sand-workflow:playwright-cli) `snapshot`、[agent-browser](sand-workflow:agent-browser) `snapshot -i`。选型与落脚本见 [box-ui-speed](sand-workflow:box-ui-speed)。

## 通用控件约定

| 类型 | 怎么认 | 可操作条件 | 操作后必验 |
|------|--------|------------|------------|
| 主按钮 / 次按钮 | role=button 或可访问名 | 非 disabled、非 loading | 文案/导航/接口副作用之一 |
| 输入框 | textbox/searchbox | 可聚焦、非 readonly | 值已写入 |
| 下拉 / 选择 | listbox/combobox | 展开后选项可见 | 选中值回填 |
| 弹层 / 抽屉 | dialog/alertdialog | 打开且焦点在内 | 关闭后焦点回退、遮罩消失 |
| 表格 / 列表 | table/list/grid | 行数据可见 | 关键列与预期一致 |
| Toast / 横幅 | status/alert 或固定区文案 | 出现即可读 | 记录文案后可继续，不盲等 |
| Tab / 分段 | tablist | 选中态可辨 | 面板内容切换 |
| 开关 / 勾选 | switch/checkbox | 可切换 | 状态翻转 |

## 状态机（通用）

- idle：主操作可点，无阻塞弹层
- loading：出现 busy/骨架/转圈，禁止重复提交
- blocked：错误弹层、网络慢提示、登录失效、强制引导
- dirty：有未提交输入或未确认注/草稿，离开前先清或确认

不确定是否可点时先取无障碍态与截图证据，再 fail-closed，不盲点。

## 项目特有层怎么挂

通用层只覆盖跨项目控件。项目特有图标、热区、咪牌/发牌、收银台字段等写入**本项目知识库**或本项目 `selectors`/`fixtures`，格式建议：

- 控件名、页面/模块、定位方式（a11y > testid > css > 像素）
- 可点/不可点样例图各至少一张
- 误判历史与纠正规则（例如「无注不判亮」）
- 关联知识点编号

不把 A 项目热区抄到 B 项目。

## 喂给机器人的最小包

1. 本技能（通用约定）
2. 本项目系统地图中的关键页与主路径
3. 本项目选择器库 / 热区样例（若有）
4. 探路时 [box-ui-speed](sand-workflow:box-ui-speed)；失败分诊 [playwright-report-triage](sand-workflow:playwright-report-triage)

## 输出习惯

短句中文。先说能不能点、依据是什么（role/name/状态），再行动。证据路径随结果给。
