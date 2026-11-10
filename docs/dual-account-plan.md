# 双号 Ultra：共享与切号方案

检索日期：2026-11-10。2026-11-10 拍板：第二个号以后再开。本次只把技能、职责模板和总控例程原文放进仓库。真实 id 映射只放 Drive，仓库里用名字占位。现网协作技能 v3.13 已替换原先的 v2.6 副本。其余待拍板项（计划族实测、超额金额、webhook 改指、Drive 是否同一 Google 用户、备用号例程策略）仍待定。

现状以总控说明为准。仓库里对得上的，注明路径。对不上或公开材料互相打架的，写「待核实」，不补故事。

## 结论

两个号都由同一人付费开通最高档 Ultra，公开合同里没有一条写明这种轮换被禁止。论坛工作人员在 2026-04-21 和 2026-08-10 说过，当时不禁止一个人持有两个 Ultra，同时写明以后可能变，账号数量极端时会触发欺诈警报。这是论坛回复，不是合同承诺。禁止的是把一个登录交给别人共用。

先别为了额度开第二个号。用户已经说明超额可以继续用、只是改计费。在这个前提下，第二个 Ultra 买到的是又一份固定月费（公开标价 200 美元/月，或年付 2000 美元，不含税），外加第二台云电脑、第二套连接器授权、第二套保险库，以及 32 个机器人的记忆和例程分叉。公开价格页没有给出 Ultra 套餐内额度值多少美元，所以算不出「第二份会员费」和「同等额度按量」谁更便宜。盈亏点要用用户自己仪表盘上的超额金额来比。

只有一种情况值得开第二个付费 Ultra：Grok Bot 的周额度用尽后，现有号上的按量或充值仍然不能让机器人继续干活。2026-11 的价格文档写的是周池包含 Grok Bot、用完可以预付继续；2026-10-01 的论坛工作人员说过 Grok Bot 周限额和 Cursor 用量分开。这两处冲突。先在现号上做一次实测，再拍板。

若仍要双号，事实来源分成三处：

- GitHub 本仓库放技能正文、机器人职责模板、例程原文、协作规则。正文里只写稳定名字，不写账号上的机器人 id 和技能 id。
- Notion 继续放各项目知识库、用例、需求、缺陷和项目记忆点。
- 每个号各自保留：服务端记忆、例程实例、云电脑、保险库、连接器授权。

记忆不做实时双向合并。同一时刻只有一个号是活号，活号可写；切号时把活号导出的 Markdown 灌进备用号。规则和项目事实冲突时，以仓库和 Notion 为准。15 分钟切号指的是备用号已经建好之后的切换，不是第一次开通。

## A. 可行性、条款与成本

### A1. 条款：同一人、两个付费 Ultra、轮换使用

查过的公开文本：

| 文本 | 日期 | 和双号相关的原文要点 |
| --- | --- | --- |
| [Terms of Service](https://cursor.com/terms-of-service) | 2026-09-03 | 第 3 条要求注册信息准确、完整、不误导，密码由注册人保管，账号下的活动由注册人负责。第 1.5 条的禁止项是逆向、转租转售、抓取、用服务训练竞争模型等。其中没有「同一人不得持有两个付费账号」或「不得用第二个付费账号承接额度」。 |
| [Grok Bot Terms](https://cursor.com/terms/grok-bot) | 2026-10-31 | 第 1.1 条：用户自行配置权限和用量上限。第 4 条：同一用户名下的机器人共享一台持久云电脑，记忆、例程、会话、凭据可以留在这台环境里；删掉一个机器人不会自动清掉共享文件和登录。全文没有禁止第二个付费账号。 |
| [Master Services Agreement](https://cursor.com/terms/msa) | 本次检索到的页面 | 客户须保证授权用户的登录不被多个人共用。这条禁止的是共用登录，不是同一人自付两个号。只有公司和工作室签了 MSA 时，这份协议才管这个号。sacks 的 Ultra 是否落在公司 MSA 下，待核实。 |
| [Grok Bot security FAQ](https://cursor.com/docs/grok-bot/security-faq) | 本次检索 | 原文：需要单独一台电脑和一套凭据时，给这个工作负载单独的 Cursor user。这是隔离建议，不是额度政策。 |
| 可接受使用政策 | 待核实 | 服务条款写明使用服务即同意 Acceptable Use Policy。本次打开 `https://cursor.com/terms/acceptable-use` 没有得到可用正文。不能断言政策里没有「禁止多开规避限额」之类的句子。 |

论坛工作人员回复（Cursor 论坛账号 kevinn，不是合同条款）：

- 2026-04-21，[Is there a $400 option?](https://forum.cursor.com/t/is-there-a-400-option/158647)。问的是再买一个 Ultra 是否违反服务条款。回复：「you are not prohibited from doing that at this time」，并写明以后可能改变。允许的例子是同一人用两个邮箱分别持有工作号和个人号。不允许的例子是一个号交给多名实习生共用。两个自用号一般不会有问题；数量极端可能触发欺诈警报。
- 2026-08-10，[Usage Guardrails](https://forum.cursor.com/t/usage-guardrails-to-stop-burning-through-the-monthly-limit-in-just-a-few-days/167802)。回复：「while account sharing is prohibited, there is no policy that prevents you from having two ultra accounts」。同一帖在 2026-10-01 又写道：「Grok bot has a weekly usage limit but it is separate from your regular Cursor usage。」

由此能说的话：

- 两个号都用真实邮箱、都由 sacks 付费、不把登录交给他人，和上述合同明文以及论坛回复是对齐的。
- 合同没有保证这种做法永远允许。服务条款第 9 条允许平台因滥用等原因暂停访问。论坛已写明政策可能变，极端多开会进欺诈检查。两个号是工作人员举过的「couple of accounts」，不是他们说的极端数量。
- 若 B 号用虚假身份注册，会碰到服务条款第 3 条的准确注册要求。
- 公司采购、报销或 MSA 是否另外禁止「公私两号轮换」，公开条款回答不了，待核实。

### A2. 公开价格：第二个 Ultra 对按量

两套计划都叫 Ultra，标价相同，额度周期和超额方式不同。用户说的是「周额度」加上「已开按量、无上限」。周额度更像现在的 X 订阅，也可能是论坛里说的 Grok Bot 单独周限额。旧版 Ultra 的包含额度按月重置。用户到底在哪一套上，待核实，看仪表盘计划名称。

公开标价（不含税），来源：[Pricing](https://cursor.com/pricing)、[Models & Pricing](https://cursor.com/docs/models-and-pricing)、[帮助中心价格说明](https://cursor.com/help/account-and-billing/pricing)、[旧版计划](https://cursor.com/docs/account/pricing/legacy-cursor-plans)：

| 项目 | 公开价格 |
| --- | --- |
| Ultra（X 订阅，当前价目表的最高个人档） | 200 美元/月，或 2000 美元/年 |
| 旧版 Ultra | 200 美元/月。价目表把它对应到 X 订阅的 Ultra，并写明对应不等于相同 |
| 包含额度的美元数或 token 数 | 公开页只写 Ultra 为 Plus 的 50 倍，Plus 为 Base。没有美元数，也没有 token 数。论坛里有用户自称旧版 Ultra 含 400 美元 API 用量，工作人员那次回复没有确认。这个数字不采用 |

超额怎么计费：

- X 订阅 Ultra：包含额度是一个周池，Cursor、Grok Bot 和 Grok 应用一起扣，每周刷新，未用完不结转。周池用完后，Cursor 自有模型按公开单价从预付额度里扣；第三方模型从第一次请求起就按 API 标价从预付额度扣，不进周池。可手动充值或开 Auto Top-up，另有每月额外用量上限。管理入口是 grok.com/dashboard/billing。来源：[Models & Pricing](https://cursor.com/docs/models-and-pricing)、[Usage and limits](https://cursor.com/help/models-and-usage/usage-limits)。
- 旧版 Ultra：两个月池（Cursor 模型、其他模型），按账单月刷新。超出部分是 on-demand，月结，按与套餐内相同的模型单价计，不加价。个人计划要在 cursor.com/dashboard/spending 里打开，并可设月度支出上限。来源：[旧版计划](https://cursor.com/docs/account/pricing/legacy-cursor-plans)、[Usage-based charges](https://cursor.com/help/account-and-billing/overages)。

周池之外、Cursor 自有模型的公开加购单价（美元 / 百万 token），来源同上 Models & Pricing，正文写明这些单价用于周池之外的加购：

| 模型 | 输入 | 缓存读 | 输出 |
| --- | --- | --- | --- |
| Grok 4.7 | 2 | 0.5 | 6 |
| Grok 4.7 Fast | 4 | 1 | 12 |
| Grok 4.6 / 4.5 | 2 | 0.5 | 6 |
| Composer 2.5 | 0.50 | 0.20 | 2.50 |
| Composer 2.5 Fast | 3 | 0.5 | 15 |

Grok 4.7 长上下文（输入超过 256k）按标准价 2 倍，Fast 加长上下文按 3 倍。第三方模型单价见同一页，这里不摘，避免和账单对不上。

旧版 on-demand 的单价页写的是「与套餐内相同、不加价」，没有单独再贴一张旧版价目。旧版用户以自己的 Spending 页为准。

算得清和算不清的部分：

- 算得清：第二个 Ultra 的固定费用是每月 200 美元，或每年 2000 美元，不含税。两号同时持有就是每月 400 美元的会员费，再加各自超出自身额度的按量或充值。额度不合并，也不结转。切到 B 之后，A 剩下的额度闲置到下次重置。
- 算不清：套餐内那一份额度值多少钱。没有这个数，就没有「同等额度走按量要花多少」的公开算术。比较方法是看现号近几个周期的超额账单：超额明显低于 200 美元，第二份会员更贵；超额稳定高于 200 美元，并且第二个号的包含额度真能被吃满，第二份会员才可能更便宜。具体差额待用户从仪表盘填数。
- 「无上限」不是价目表上的产品承诺。X 订阅靠预付余额和每月额外用量上限；旧版靠是否打开 on-demand 以及支出上限。上限设得很高时，账单可以一直涨。支出上限到达后会停掉额外用量，但文档写明执行不是瞬时的（[Spend limits](https://cursor.com/help/account-and-billing/spend-limits)）。

建议：

1. 先在现号实测。周额度用尽后，不切号，发一条 Grok Bot 任务。能继续且只是计费，就维持单号，用支出上限或每月额外用量上限控制账单。
2. 实测结果是机器人直接停、充值也不恢复，再考虑第二个付费 Ultra。那时候买的是另一份可用的机器人额度，不是去绕一条已经写明的禁令。
3. 双号的隐性成本不在标价里：两台云电脑、两套授权、切号时的人工、例程双开造成的重复测试和重复日报。这几项即使用量上划算，也会吃掉节省的钱。

## B. 双号时的单一事实来源

备用号必须先建完，才能谈 15 分钟切换。第一次开通要建大约 32 个机器人、逐个授权、重登保险库，不在 15 分钟里。

### B1. 三处分别放什么

| 事实 | 放哪 | 原因 |
| --- | --- | --- |
| 技能正文，含核心协作技能 | 本仓库 `grokbot/skills/<稳定名>/SKILL.md` | 已有备份骨架。现网以机器人工具写入 `/home/box/agent-data/workflows/<slug>/SKILL.md`，slug 按号变化 |
| 机器人名称、职责、规则 | 本仓库 `grokbot/bots/`，扩成完整花名册模板 | 现仓库只有四个角色加升级技能。约 32 个机器人的描述在账号的 profile.json / settings.json 里，要先从活号导出，不能在仓库里编 |
| 例程原文（cron、提示词、目标机器人的稳定名） | 本仓库新建 `grokbot/routines/` | 例程实例在服务端，按机器人分，只能用工具创建。原文进仓库，实例每号重放 |
| 协作红线和仓库约定 | 继续用 `grokbot/skills/` 与根目录 `AGENTS.md` | 不另起一套规则 |
| 稳定名到各号 id 的映射 | Google Drive 备份目录里的 `id-map.yaml` | id 会变。仓库可见性待核实，映射先跟现有每日备份走，不进 Git |
| 映射的空模板 | 以后可加 `grokbot/mapping/id-map.example.yaml`，账号槽留空 | 只示范字段，不填真实 id、邮箱、webhook |
| 项目知识、用例、需求、缺陷、项目记忆点 | 各项目 Notion | 总控已确认换号不丢。`grokbot/README.md` 已规定业务上下文以 Notion 为准 |
| 哪一个号是活号、最近一次切号时间 | Drive 上的 `ACTIVE.txt` | 两个号都要能读到同一份。不写进 Git，避免和密钥或账号邮箱缠在一起 |
| 记忆 profile / journal / shared_* | 服务端为运行副本；Drive 上的 Markdown 为切号介质 | 没有公开的导入导出接口。设置里的 import-memory 能力见 B3 |
| 云电脑工具链 | 每号各自的云电脑 | 用仓库里的 `tools/bootstrap_bot_computer.sh` 重建。`/workspace/qa/qa-ready.sh` 不在本仓库，总控说周日大备份含环境脚本，以备份里的脚本为准 |
| 保险库登录、连接器令牌 | 每号各自授权 | Notion 多工作区、Google Drive、GitHub、Atlassian、Figma 都要在 B 上由用户重授权。令牌不进 Git、聊天、记忆 |
| 测试账号明文 | `/workspace/qa/secrets/`、用户 Windows 本地、Notion 测试账号页 | 两台云电脑不共享磁盘。拷贝由用户走自己的安全通道。禁止进 Git、聊天和记忆 |
| CI 通知地址 | GitHub 仓库密钥，只在 GitHub 设置里改 | 变量名见 B6。一个密钥只能指向当时的活号 |

2026-11-10 的现网快照已核对：核心协作技能的稳定名是「项目机器人协作与故障闭环」，文内版本 v3.13，目录仍是 `grokbot/skills/project-bot-collab/`。数字 slug 只留在 Drive 的映射里。

技能正文继续遵守现网 v2.6 已有的写法：通用技能里不写死机器人 id。总控深链 `grokbot://app/v1/agent?id=<执行方稳定id>` 在渲染到某个号时再填该号的 id。

### B2. 名字映射，把两号的 id 隔开

稳定名是人认的名字，例如「总控」「知识库总控」「日报」。机器人 id、技能 slug、例程 id 都是账号本地值。

模板里只允许两种占位符：

- `{{bot:总控}}`：渲染成该号的机器人 id
- `{{skill:项目机器人协作与故障闭环}}`：渲染成该号的技能 slug

描述、例程提示词、深链都从模板渲染。已经写进 A 号描述里的裸 id，在阶段 1 改模板时清掉，并在 A 上读回，确认机器人仍能找到队友。B 从渲染结果创建，不复制 A 的 profile.json。

Drive 上的 `id-map.yaml` 用下面的形状。示例里的值是空的：

```yaml
version: 1
bots:
  - stable_name: 总控
    template: grokbot/bots/总控.md
    accounts:
      A: { agent_id: "" }
      B: { agent_id: "" }
skills:
  - stable_name: 项目机器人协作与故障闭环
    template: grokbot/skills/project-bot-collab/SKILL.md
    repo_version: ""          # 与 SKILL.md 文内版本一致
    accounts:
      A: { slug: "", version: "" }
      B: { slug: "", version: "" }
routines:
  - stable_name: 日报
    template: grokbot/routines/日报.md
    target_bot: 日报
    accounts:
      A: { routine_id: "", enabled: false }
      B: { routine_id: "", enabled: false }
```

解析规则：

- 按 `stable_name` 查找，查不到就停，不按相似名字猜测。
- 一个稳定名在一个号上只对应一个 id。导出时若发现重名，先停下来让用户改名。
- 渲染后的描述若仍含 `{{` 或含另一个号的 id，视为失败，不写入。
- 技能按稳定名和文内版本写入。数字 slug 只是该号的存储名，不进 Git，换号后也不必复用。

### B3. 记忆怎么同步

公开说明（[What your Bot remembers](https://cursor.com/help/grok-bot/memory)、[设置说明](https://docs.x.ai/grok-bot/settings-and-notifications)）：

- 每个机器人有自己的记忆；少数关于用户本人的事实在该账号的机器人之间共享。
- 记忆不是权威来源。会变的事实放在源系统里。
- 设置 → General → Import → Start Import：把一段从其他助手得到的文本粘进去，Add to Memory 后送到主机器人并打开那个聊天。文档写的是「从另一个助手导入到主机器人」，不是 32 个机器人的 profile/journal 批量接口。
- 桌面已登录多个号时，账号菜单有 Switch account，也可以 Add account。这只切换客户端登录，不搬运云电脑和记忆。

和总控现状合在一起：服务端记忆只能靠机器人工具读写；没有公开批量导入导出接口；设置里的 import-memory 不能当作双号同步方案，除非阶段 2 证实它能按机器人写入 profile 和 journal。在证实之前，导入通道是活号上的记忆工具。

同步方式是单活写入，切号时单向灌入，不做双活合并。

导出格式沿用现有每日备份的 Markdown，补上固定文件头，便于读回。一个机器人一个文件，共享记忆另两个文件：

```markdown
---
kind: profile
bot_stable_name: 总控
account_alias: A
exported_at: 2026-11-10T23:55:00+08:00
entry_count: 0
---

## entry
updated_at: 2026-11-10T23:50:00+08:00
body: |
  这里是一条记忆正文。
```

`kind` 只取 `profile`、`journal`、`shared_profile`、`shared_journal`。`journal` 按时间追加。`profile` 是稳定事实。打包前沿用现有备份的剔除密钥步骤。导出文件进 Drive，不进 Git。

冲突以谁为准：

| 内容 | 谁为准 |
| --- | --- |
| 技能、职责、规则、例程原文 | 仓库模板 |
| 项目知识、缺陷、进度、测试账号页的存在 | 该项目 Notion |
| 切号当时的工作日志 | 切出号这次导出的 journal，按时间追加到切入号，不覆盖切入号已有的更晚条目 |
| 机器人 profile 里的稳定事实 | 仓库模板和 Notion 里已有的同题事实。两边都没有时，采用导出文件里 `updated_at` 更新的一条 |
| 同一事实两边句子互相矛盾 | 不自动覆盖。总控列出差异，等用户选。在此之前切入号保持原句 |
| shared_profile / shared_journal | 先灌共享记忆，再灌各机器人的 profile，最后追加 journal |

频率：

- 切号前强制导出一次，不依赖当晚 23:55 的定时备份。
- 每日 23:55 小备份、周日大备份保持不变，作为恢复点。
- 平时不把备用号的记忆往回合并。备用号的机器人不聊天、不跑例程，避免产生第二份日志。

导入后读回：条数与 `entry_count` 一致，最新一条 `updated_at` 一致，抽三条正文一致。对不上就停在切号流程，不宣布可用。

### B4. 切号清单

前提：B 已完成阶段 3；Drive 上有当天的 id-map；A、B 都授权了同一个 Google 用户，备份能写进同一 Drive。Google 用户是否已经是同一个，待核实。目标时钟从「A 开始收尾」到「B 总控读回通过」。

切前，在 A 上，大约 5 分钟：

1. 总控把进行中的写操作收尾，或把检查点写进对应项目 Notion。未写完的不记成完成。
2. 用工具停掉 A 上全部例程，并读回确认都是停用。避免切走之后日报、巡检、备份还在 A 上跑。
3. 立刻做一次与每日小备份相同的打包：技能、记忆 Markdown、花名册 profile/settings、总控例程原文、`RESTORE.md`。打包前剔除密钥。
4. 若有技能改动还没进仓库，把 diff 放进这次 Drive 包，事后再开 PR。紧急切号不等待 PR 合并。
5. 写 Drive `ACTIVE.txt`：`switching-from=A`，时间用北京时间。
6. 抽查压缩包文件名和 `RESTORE.md`，确认没有 `/workspace/qa/secrets` 和令牌字段。

切后，用户和 B 的总控，大约 10 分钟：

1. 用户在 Grok Bot 桌面 Switch account 到 B。这一步只能用户做。
2. 若 B 的云电脑是新的或刚被重置，用户先放好 `/workspace/qa/secrets/`（只走用户自己的通道），再跑备份中的环境脚本和：

```bash
bash tools/bootstrap_bot_computer.sh https://github.com/bibuat1-stack/qa-agent-team
```

云电脑没被重置、仓库和虚拟环境还在时，跳过安装，只 `git pull`。

3. B 的总控读取仓库模板、Drive 上的 `id-map.yaml` 和刚导出的记忆包。
4. 按稳定名把技能写入 B 的 workflows，版本与仓库文内版本一致。
5. 渲染描述并写回 B 的 `profile.json`、`settings.json`。只填 B 列的 id。
6. 按 B3 的顺序灌入记忆，然后读回。
7. 按 `grokbot/routines/` 核对 B 的例程：缺的用工具创建，然后只启用应在活号上跑的那些。再读 A，确认 A 的例程仍是停用。
8. 写 Drive `ACTIVE.txt`：`active=B`。
9. 读回验证通过后，才把活交给 B。

读回验证，缺一项就不算切完：

- 总控能读到本仓库 `main` 上的技能文件，文内版本与 B 上读回的版本一致。
- 抽样一个项目机器人，复述的职责与模板一致，队友指向 B 列的 id。
- 抽样一个项目 Notion 入口能打开。
- 例程条数与仓库原文一致，A 全停、B 该开的已开。
- `/workspace/qa/secrets/` 下预期文件名存在。只核对文件名，不打印内容。
- 记忆读回符合 B3。

脚本化边界：第 2 步的 bootstrap 已是仓库脚本。停例程、灌记忆、读回仍靠机器人工具。切号清单本次不脚本化。把现网技能、职责模板和例程原文收进仓库，用 `tools/export_grokbot_roster.py`：只读云电脑来源，名字占位写进仓库，真实 id 写到仓库外的 `--id-map`。

切号后 CI 仍会把失败摘要打到仓库密钥 `GROKBOT_WEBHOOK_URL` 指向的那个机器人。A 没额度时，这个通知到不了人。改密钥是用户在 GitHub 设置里做的，可能超 15 分钟，不挡开工，但要记在切号结果里：通知还指向旧号，直到密钥改完。

切回 A 用同一清单，方向相反。回滚点是切前那份 Drive 包。

### B5. 备份与现有节奏的关系

每日 23:55 小备份、周日大备份继续由活号执行。备用号不跑备份例程，避免两台机器同时写同一个 Drive 对象。

建议的 Drive 布局（目标布局，不是已证实的现状）：

```text
QA-Backup/
  ACTIVE.txt
  id-map.yaml
  A/2026-11-10-small/
  B/2026-11-10-small/
  weekly/2026-11-09/
```

周日大备份继续包含环境脚本、30 天快照、附件文档，并带上当时的 `id-map.yaml`。包内仍然剔除密钥。

### B6. 凭据边界

下面只列名字。值不进 Git、不进本文、不进记忆、不进聊天、不进 Drive 备份包。

| 名字 | 放哪 |
| --- | --- |
| `ENVIRONMENT` `TEST_ENV` `API_BASE_URL` `UI_BASE_URL` `TEST_RUNNER` `NOTIFY_ON_PR` | 运行环境或 GitHub 仓库变量。地址类可以按现有 `config/environment.py` 的非密钥约定 |
| `API_TOKEN` `UI_USERNAME` `UI_PASSWORD` | 云电脑 `/workspace/qa/secrets/`、用户 Windows 本地、GitHub Actions 密钥 |
| `GROKBOT_WEBHOOK_URL` `GROKBOT_WEBHOOK_KEY` | GitHub Actions 密钥。切活号时由用户改指向 |
| `CURSOR_API_KEY` | 只在走 `tools/ask_cursor.py api --send` 的那台电脑的环境里 |
| Notion / Google / GitHub / Atlassian / Figma 的 OAuth 令牌 | 该号的连接器授权，用户在 B 上逐个点授权 |
| 保险库里的网站登录和支付卡 | 该号的保险库，用户重登 |
| 测试账号明文 | `/workspace/qa/secrets/`、Windows 本地、Notion 测试账号页 |

`ask_cursor.py` 的每日升级额度账本在云电脑 `/workspace/qa/escalations/`，随电脑走，不随 Cursor 账单走。B 是一台新电脑时，这个账本从头计。不要把它当记忆去同步。

## C. 分阶段落地

每一阶段都可单独停。停在任一阶段，活号仍是 A。

### 阶段 0：拍板前的实测

- 改哪些文件：无。
- 谁做：用户本人。在现号周额度用尽或接近用尽时，看仪表盘计划名称，并给总控发一条普通任务。
- 验证：记下三件事。计划名称是旧版 Ultra 还是 X 订阅 Ultra。机器人是否仍能调用工具并完成回复。这一周期超额或充值金额是多少。
- 回滚：无改动。
- 通过标准：用 A2 的规则决定维持单号，或进入阶段 1。维持单号时，本文到此为止，不必建 B。

### 阶段 1：让仓库追上现网

对单号也有用。2026-11-10 快照已导出：51 个技能、32 个机器人模板、总控 4 条例程。快照里的机器人目录是 32 个，不是事先说的 33 个。其他机器人的例程在 `grokbot/routines/README.md` 标为待各机器人自报。第二个号未开。

- 改哪些文件：
  - 从活号导出后覆盖 `grokbot/skills/**/SKILL.md`，先核对 v3.13 与 `project-bot-collab` 是不是同一技能。
  - 把约 32 个机器人的职责导出成 `grokbot/bots/<稳定名>.md`，裸 id 改成 `{{bot:名}}` 和 `{{skill:名}}`。
  - 新增 `grokbot/routines/<稳定名>.md`，内容来自总控已备份的例程原文。
  - 新增 `grokbot/mapping/id-map.example.yaml`，结构同 B2，值全空。
  - 更新 `grokbot/README.md` 的目录说明。真实 `id-map.yaml` 放 Drive。
  - 不改 `data/`，不改 `.github/`。
- 谁做：总控导出；用户确认导出里没有密钥；Cloud Agent 或自动化工程师开一个只含 `grokbot/` 的 PR。按仓库规则，仅技能备份加 README 说明可以由 Cloud Agent 在 CI 通过后合并；这次若带上花名册和例程，超出「只含 skills」的范围，等人审核。
- 验证：渲染脚本或人工替换后，抽 3 个描述，不含 A 的数字 id，职责与现网一致。`grep` 仓库新增文件，确认没有令牌、密码、Cookie、webhook URL。总控读回仓库副本，确认版本号与现网一致。
- 回滚：还原该 PR。A 上的现网技能和描述在合并前不要删。

### 阶段 2：在一个机器人上试记忆导入

- 改哪些文件：无。可选把导出文件头样例留在 Drive 的 `RESTORE.md`，不进 Git。
- 谁做：总控用记忆工具写一条不含秘密的试验 profile，再读回。用户看设置里的 import-memory，确认它是否只能进主机器人。
- 验证：记下工具是覆盖还是追加，能否指定某个机器人，而不是只能写主机器人。读回正文与写入一致。试验条目随后删掉，再读回确认已删。
- 回滚：删除试验条目。失败则 B3 的导入通道维持「待核实」，阶段 4 不承诺记忆 15 分钟内对齐，只承诺技能、描述和例程。

### 阶段 3：开通 B

全是用户操作，机器人不能代登录。

1. 用另一个真实邮箱注册，开通 Ultra，并在桌面 Add account。付费档与 A 相同。
2. 逐个授权 Notion 各工作区、Google Drive（与备份同一个 Google 用户）、GitHub、Atlassian、Figma。授权范围与 A 对齐，不额外扩大。
3. 保险库里的被测站登录由用户重登。
4. 用户把 `/workspace/qa/secrets/` 拷到 B 的云电脑。不经 Git，不经聊天。
5. 跑 B4 里的 bootstrap。`qa-ready.sh` 从周日大备份取出，本仓库没有这份文件。
6. 按模板创建机器人、写入技能、创建例程，例程先全部停用。
7. 把 B 列 id 填进 Drive 的 `id-map.yaml`。

- 验证：B 的总控能读仓库和抽样 Notion。技能版本读回与仓库一致。例程存在且为停用。密钥目录只核对文件名。A 的例程和记忆没有被这一步改动。
- 回滚：B 的例程保持停用，继续只用 A。取消 B 的订阅须在续费前至少 24 小时操作，见服务条款第 4.4 条。已创建的 B 机器人可先隐藏，不必立刻删除；删除会清掉该机器人记忆且不可恢复。

### 阶段 4：按清单演练一次

- 改哪些文件：无。演练若要改总控提示词，回到阶段 1 的 PR 流程。
- 谁做：用户切号；A、B 的总控按 B4 执行。
- 验证：从 A 收尾到 B 读回通过的时间。目标是 B 已建好的前提下 15 分钟内。同时确认没有双开例程（日报、备份、巡检只在活号）。演练任务用一条无副作用的读操作，例如总控读仓库版本并复述。
- 回滚：用演练前的 Drive 包按相反方向切回 A，启用 A 的例程，停用 B 的例程，把 `ACTIVE.txt` 改回 A。若演练把 A 的记忆写脏，用切前的 Markdown 读回覆盖试验条目。

### 阶段 5：日常

- 改哪些文件：技能或职责有变时，当天更新 `grokbot/skills` 或 `grokbot/bots` 并走 PR。id-map 只改 Drive。
- 谁做：活号上的机器人改现网；用户审 PR。切号仍按 B4，由用户执行登录和密钥改指。
- 验证：每周抽一次，仓库文内版本与活号技能版本一致；`ACTIVE.txt` 与桌面当前登录一致；备用号例程为停用。
- 回滚：活号改坏时，用上一份 Drive 小备份和仓库上一个合并提交恢复。备用号在恢复完成前保持停用。

## 待核实

1. Acceptable Use Policy 全文。本次公开页没有给出可用正文。
2. sacks 的 Ultra 是否受公司 MSA 或报销制度约束。
3. 仪表盘计划名称，以及周额度用尽后 Grok Bot 能否靠现有按量或充值继续干活。
4. 近几个周期超额金额，用来和 200 美元比较。
5. 核心协作技能是否同一份：已核对，是。稳定名「项目机器人协作与故障闭环」，仓库文内版本现为 v3.13。数字 slug 不进 Git。
6. 设置里的 import-memory 能否按机器人写入 profile 和 journal，以及记忆工具是覆盖还是追加。
7. `/workspace/qa/qa-ready.sh` 的正文只在云电脑和周日大备份里，不在本仓库。
8. 每日备份的 Drive 目录名，以及 A 的 Google 授权能否被 B 用同一个 Google 用户接上。
9. 仓库可见性：2026-11-10 查看 GitHub，本仓库是 Public。真实 id 仍然不进 Git。职责模板里有项目分工和 Notion 入口，合并前若要避免公开，需由用户把仓库改为 Private。
10. 花名册人数：快照内 32 个机器人，稳定名已写入 `grokbot/bots/`。与事先说的 33 个不一致，缺的那一个待总控核对。
