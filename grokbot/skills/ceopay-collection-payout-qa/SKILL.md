---
name: ceopay-collection-payout-qa
description: >-
  测 T8T游戏 下 CEOpay
  代收代付（代收订单、代付订单、购买订单、UPI钱包、USDT、商户余额、报表、风控争议单）时使用。开工、写验收、核状态机、做对账抽检、留痕前先加载。只服务
  CEOpay，不用于 AntPay、多站点彩票、nova、M3、GO。规则以 Notion「CEOpay ·
  测试知识库」为准，本技能只做骨架和索引，不存业务密文。
---
# CEOpay 代收代付 QA（v1.0，2026-11-10 用户批准 B8）

> 只读扫库日期 2026-11-10（Asia/Shanghai）。库内规则更新后以 Notion 为准，本技能只做骨架和索引。
> 规则来源一律标 Notion 页标题与链接。库里没有依据的只放「待确认」，不当验收标准。
> 知识点页正文多为空，依据是该页属性「要点」与「状态」。状态为待确认的条目只能当线索。

## 0. 适用与边界

- 适用机器人：T8T测试执行、T8T站点走查、T8T提单回归、T8T需求分析、T8T知识库总控。
- 只管 CEOpay 子库：[CEOpay · 测试知识库](https://app.notion.com/p/40e9db9f9b9681419798fd1d4e2fb8ec)。
- AntPay 库待建。AntPay 内容先问用户，不写进 CEOpay。
- 入库交「T8T知识库总控」（id: {{bot:T8T知识库总控}}），执行号不直接写库。
- 协作与故障按 {{skill:项目机器人协作与故障闭环}}。开工 {{skill:测试记忆-开工}}，影响面 {{skill:测试记忆-影响面}}。

## 1. 开工三步

1. 读 [系统地图](https://app.notion.com/p/40e9db9f9b968198b63bf4b640d921b7) 的模块耦合、核心业务对象、耦合热点、待确认。
2. 按模块查 [知识点](https://app.notion.com/p/1f5ed790d64140098a6fc6cff5ce4981) 与 [缺陷](https://app.notion.com/p/ffd7d73793974b9ea25fbf8ee02f3aa6) 未关项。看 [测试日志](https://app.notion.com/p/cbd4c99fb8934736b1ab9de4dd296593) 最近一篇的「没做完」「下一步」。
3. 复述：任务范围、验收标准（带 KP 编号）、禁做项、回报位置。

耦合热点优先回归（来源：系统地图）：会员余额、代付订单、购买订单、商户余额、UPI钱包账户。
枢纽度最高的是 KP-4 代付订单、KP-5 购买订单（来源：[知识图谱](https://app.notion.com/p/40e9db9f9b968148b5f4dae88dc50523)）。

## 2. 验收骨架（每个任务按此填）

| 栏 | 填法 |
|---|---|
| 对象 | 代收单 / 代付单 / 购买单 / USDT单 / UPI账户 / 商户余额 / 会员余额 |
| 前置状态 | 用库里的状态码，写 KP 编号 |
| 动作 | 页面操作或接口名，写 KP 编号 |
| 期望 | 只写库里有的。无依据写「待确认」 |
| 联动核对 | 关联单状态、余额、账变、商户流水、报表、风控争议单 |
| 证据 | 截图或接口摘要（脱敏），订单号可留，个人信息不留 |
| 结论 | 通过 / 失败 / 阻塞 / 未测 / 未验证 |

场景至少覆盖：正向、异常、边界、联动（与 [测试用例](https://app.notion.com/p/9e8bc8f3a6384ca4bab93ce0b55fdd63) 的「场景」选项一致）。

## 3. 状态机核对

### 3.1 代付订单

状态码：0 待处理、1 已支付、3 已提交、4 处理中、5 驳回。来源 KP-4「代付订单」(https://app.notion.com/p/40e9db9f9b968105b0c4e792b62253ee)，已确认。

| 迁移或约束 | 依据 |
|---|---|
| 会员领单用风控正常的已绑 UPI | KP-31「代付订单｜渠道代付领单」(https://app.notion.com/p/40e9db9f9b9681deb5dbd89016774597) |
| 会员有未完成买单不可领单，错误码 1066 | KP-53 (https://app.notion.com/p/40e9db9f9b96819d9c76ea8b95aa56d7) |
| 提交 UTR 要求 UTR 唯一，重复报 1379，状态不允许报 1365 | KP-55 (https://app.notion.com/p/40e9db9f9b96810680ddc880ad89dbee)，KP-32 (https://app.notion.com/p/40e9db9f9b9681589f1ce4048e4ebbe8) |
| 需补款前置：代付与购买单均为已提交(3)，且订单金额大于账单金额 | KP-51 (https://app.notion.com/p/40e9db9f9b9681a0aa9edfc223149259)，KP-33 (https://app.notion.com/p/40e9db9f9b96812ebe97d33c68d0c6a9) |
| 补款金额匹配出款账单则代付免审成功，否则转人工补单。未匹配返回 data:false | KP-56 (https://app.notion.com/p/40e9db9f9b9681be8f02c4aca064ae58)，KP-36 (https://app.notion.com/p/40e9db9f9b968141bd72c9f09f88b9c2) |
| 人工创建：代付 0 且购买单 5 驳回，两单匹配且购买单已绑会员。成功后代付变 1、购买单变 1 | KP-52 (https://app.notion.com/p/40e9db9f9b9681b78098e94ce67d1c6b)，KP-34 (https://app.notion.com/p/40e9db9f9b9681c98046e8b4492ed2eb) |
| 会员取消计入取消次数 | KP-35 (https://app.notion.com/p/40e9db9f9b9681b78114d3c349e9a2df) |
| 出售金额必须是 100 的倍数，否则 1090。余额不足报 1016 或 1079 | KP-58 (https://app.notion.com/p/40e9db9f9b968121ada7eeefb6908dfc) |
| 超时取消与 UTR 撮合由定时任务驱动 | KP-49「系统配置｜定时任务」(https://app.notion.com/p/40e9db9f9b968130ba53f75281c777fe) |

待确认：
- 状态码 2 的含义库里没有。
- 可取消状态有冲突：KP-35 写「仅待处理/处理中」，KP-54 (https://app.notion.com/p/40e9db9f9b9681fdbaf0d24f562cc109) 要点写「错误码1384仅待处理可取消」。按冲突上报，不自己选。
- 待处理单多久超时取消库里无规则。2026-11-09 测试日志只记单样本观察，未成规则。
- 自动拆单的拆分对象是推断。KP-61 (https://app.notion.com/p/40e9db9f9b9681869e78f66ff15b4b8e) 状态待确认。

### 3.2 购买订单

会员领单产生，用 withdrawOrderNo 关联代付单。来源 KP-5「购买订单」(https://app.notion.com/p/40e9db9f9b9681609356c3ea45133548)。
库内出现的状态：3 已提交（KP-51）、5 驳回、1（KP-34 成功后状态，名称未写）。
待确认：购买单完整状态码表。

### 3.3 代收订单

含 UTR、浮动金额、回调状态，是商户收款入口。来源 KP-3「代收订单」(https://app.notion.com/p/40e9db9f9b9681b9abecdc4331dbfef1)。
代收与代付列表共用接口，channelCode 区分入口（8001 商户侧，7001 订单管理侧，含义待开发确认）。来源 KP-66 (https://app.notion.com/p/40e9db9f9b968123b4f3cfc01519d38e)，KP-21 (https://app.notion.com/p/40e9db9f9b96818c8c1ef2a8435825e2) 待确认。
待确认：代收订单状态码表、回调状态取值。

### 3.4 USDT 订单

状态：1 处理中、2 已支付、3 超时取消、4 驳回。来源 KP-10 (https://app.notion.com/p/40e9db9f9b9681ec93b8e31ea3772247)。
- 已有未完成 USDT 单不可再下单，超时按 usdtOrderCountdown。来源 KP-57 (https://app.notion.com/p/40e9db9f9b96817389e0f60e56d72850)，KP-14 (https://app.notion.com/p/40e9db9f9b968107a172ebf5cb368b11)。
- usdtAmount 大于 0，向下取 2 位。来源 KP-38 (https://app.notion.com/p/40e9db9f9b9681548fabcdb004909766)。
- 订单 exchangeRate 取自 usdtWithdrawRate。来源 KP-13 (https://app.notion.com/p/40e9db9f9b9681acbbc4ccbbb2ebe0ef)。
待确认：USDT 与余额的联动（系统地图待确认项）。

### 3.5 UPI 钱包账户（通道侧）

accountStatus：1 暂停、2 活跃、3 锁定、4 受限、5 使用中。来源 KP-6 (https://app.notion.com/p/40e9db9f9b968138bd3cc1957b53ad4b)。
- 提交 UTR 返回 UPI 是否活跃。来源 KP-32。
- UPI 被置暂停且会员在线时经 WebSocket 推送 INACTIVE_PLAYER_CHANGE。来源 KP-30 (https://app.notion.com/p/40e9db9f9b9681f293dbdc27246ae4e7)。
- 后台禁止手机 UPI 时须输 UPI ID。来源 KP-79 (https://app.notion.com/p/4119db9f9b9681cd9d89d61cbde4f637)。
- UPI 配置含权重、限额、浮动等。来源 KP-16 (https://app.notion.com/p/40e9db9f9b968124a852db4d2339fff6)。
待确认：权重与限额如何影响领单分配。

### 3.6 争议单（风控）

类型：1 金额不符、2 UPI 失活、3 锁定，含超时等级。来源 KP-9 (https://app.notion.com/p/40e9db9f9b96811b88ced80ec9a4ea97)。
trade_type + order_no + dispute_type 相同只保留一条。来源 KP-59 (https://app.notion.com/p/40e9db9f9b9681d39142d740ff396fb8)。
风控规则 17 条全开。来源 KP-8 (https://app.notion.com/p/40e9db9f9b96812cb2b3e798554c6056)。
待确认：每条风控规则的触发阈值。

## 4. 回调核对

- 商户回调重发有 resendCallback、manualCallback、batchCallback，回调到订单所属商户地址。来源 KP-37 (https://app.notion.com/p/40e9db9f9b968155bbd1e247e2665b10)。
- 抽检：重发后订单回调状态变化、只发往所属商户、批量重发不串商户。
- 待确认：回调签名规则、自动重试次数与间隔、幂等要求、回调状态取值。库里都没有。
- App 报文加密与 sign 算法未文档化。来源 KP-67 (https://app.notion.com/p/40e9db9f9b9681a3b600f5647346e90a)，待确认。

## 5. 对账抽检清单

库里没有成文的「对账规则」页。以下只用已确认的字段与恒等式做抽检，结论写「抽检一致 / 不一致」，不写「对账通过」。

| 抽检项 | 依据 |
|---|---|
| 会员余额 realBalance + tradingBalance = balance，virtual 与 unsaleable 恒为 0 | KP-1 (https://app.notion.com/p/40e9db9f9b9681c38c8fca7b04cccf12) |
| 账变记录前额 + 变动额 = 后额，orderNo 与 utr 可回查订单 | KP-2 (https://app.notion.com/p/40e9db9f9b968142805bce4a6b63821a) |
| 商户流水前后金额与手续费可对上 merchant.amount | KP-7 (https://app.notion.com/p/40e9db9f9b9681c0a611f2b60360e3c4) |
| 代收、代付订单改变商户余额 | 系统地图「核心业务对象」 |
| 平台、商户、代理日报表与当日订单抽样一致 | KP-42 (https://app.notion.com/p/40e9db9f9b9681d0b01af63d43b830b4) |
| 报表日期参数两种风格，查询别用错 | KP-64 (https://app.notion.com/p/40e9db9f9b9681b2bafcc74271eb81b0) |
| 代理佣金按会员与代理维度日统计，commission_status 1 未发 2 已发 | KP-43 (https://app.notion.com/p/40e9db9f9b9681e38779e68668a0df78)，KP-11 (https://app.notion.com/p/40e9db9f9b968127bd93c8cd4cbb23e4) |
| 代付赠送率按金额档展示 | KP-17 (https://app.notion.com/p/40e9db9f9b96816eb506e5bbcd7ef4f6) |

待确认：商户手续费计算口径、报表统计口径与时区切日、代收单与商户余额入账时点。
相关未关缺陷：「代理佣金比例单位不一致」(https://app.notion.com/p/4109db9f9b968121a521f3dcbb530c7f)、「平台报表印度数字格式与其他页不一致」(https://app.notion.com/p/4109db9f9b9681a5bab6c885f60d98b1)。

## 6. 脱敏留痕约定

- 账号、密码、token、验证码、谷歌码、商户密钥、bot token 一律不进聊天、Notion、记忆、截图。来源：库首页说明「账号密码不进库」，测试日志 2026-11-07「安全」段。
- 截图前遮掉：手机号、邮箱、UPI ID、真实姓名、密钥类字段。订单号与 UTR 可留，用于回查。
- 已知敏感外露点，只记现象不复制值：
  - KP-65 Showdoc 示例含疑似真实 JWT (https://app.notion.com/p/40e9db9f9b9681e4afdff195d8c565fe)
  - KP-73 客服配置明文显示 TG bot token (https://app.notion.com/p/40e9db9f9b9681f580b9f3e4e9ff1e00)
  - KP-74 代理列表明文谷歌密钥且接口返回 password/secretKey (https://app.notion.com/p/40e9db9f9b9681c6b2b9c548ab18bbb8)
  - 缺陷「商户 API Secret 等明文敏感」(https://app.notion.com/p/4109db9f9b9681c2a404e2ab30e69fc5)
- 抓包或 HAR 外发前按 evidence-hygiene 技能脱敏。
- 测试日志按库内五段写：做了什么、发现、知识变更、没做完、下一步。
- 测完清理现场，测试造的单在日志里列单号。

## 7. 高风险禁做（未经用户当次授权）

| 禁做 | 依据 |
|---|---|
| 人工存提（增 7 / 减 8），库里标危险操作 | KP-39 (https://app.notion.com/p/40e9db9f9b9681aeab39deae6d60a86b) |
| 重建报表 | KP-42 |
| 手点执行定时任务 | KP-49 |
| 代理上下分、重置密码、重置谷歌 | KP-69 (https://app.notion.com/p/40e9db9f9b9681c69ba8ef092365bd72)，KP-60 (https://app.notion.com/p/40e9db9f9b968117a136c190519fb8e0) |
| 模拟渠道入金或出款（会生成真实待处理单） | KP-41 (https://app.notion.com/p/40e9db9f9b9681d0bcd5eb8318d02c7f)，测试日志 2026-11-09 |
| 改风控配置、UPI 配置、支付配置、自动拆单 | KP-8、KP-16、KP-18 |
| 在灰度或生产环境做任何写操作 | 资料「CEOpay 环境入口（测试/灰度/生产）」(https://app.notion.com/p/40e9db9f9b9681089d57ec379659f4d7) 只说明分环境，写操作授权规则待确认 |
| 自己改已确认知识点 | 测试日志 2026-11-09「禁止自动改已确认条目」 |

越权核对：代理与商户角色只能看自身数据，越权应返回无权操作。来源 KP-60。

## 8. 待确认总表（交用户或开发）

1. 代付状态码 2 的含义。
2. 代付可取消状态：KP-35 与 KP-54 冲突。
3. 购买单、代收单完整状态码表与回调状态取值。
4. 回调签名、重试、幂等。
5. channelCode 7001/8001 含义（KP-21）。
6. 后台 token expires_in 单位（KP-22）。
7. App sign 与加密算法（KP-67）。
8. 自动拆单作用对象（KP-61）。
9. USDT 与余额联动。
10. 待处理代付超时规则。
11. 对账口径：手续费、报表切日时区、入账时点。
12. 2026-11-09 测试日志三条本地实测未入库：checkChannelPayout 补分主路径、simulateChannelPay 未开通渠道报 1369、待处理单观察。是否补入 KP-41 或新建待确认条目，等用户定。
13. 灰度与生产环境的写操作授权规则。
