# T8T 生产前台安全路径脚本

三站共用这一套，不按站点复制三份。只覆盖已经打开过、页面上有判定信号的安全步骤。这里没有正式用例编号的项，脚本记「待确认」，不当验收通过。

本目录不记录某一次走查的结论，也不把以往某站的回收结果写成通过。

## 登记

| 文件 | 作用 |
| --- | --- |
| `run_main_flow.py` | 入口。`--site` 选 yy567、muskan、paglu 或 all，`--step` 选 login、nav、wingo、recall、switch、all |
| `sites.py` | 生产入口。YY567、MuskanClub、PagluGame |
| `credentials.py` | 读密码。读不到就退出码 2 |
| `browser_steps.py` | 清会话、登录、底栏、进 Win Go、回收、换厂商 |
| `verdicts.py` | 回收判定。不看页面 |
| `test_recall_verdict.py` | 只检查判定函数，不访问生产 |

## 怎么跑

在仓库根目录、已安装依赖的环境里：

```bash
export T8T_PASSWORD='从本机账号资料读取，不要写进仓库'
python grokbot/scripts/t8t/run_main_flow.py --site yy567 --step login
python grokbot/scripts/t8t/run_main_flow.py --site muskan --step all
```

Muskan 不传 `--phone` 时用 9959950001。`--phone` 只能是 9959950001、9959950002、9959950003。

密码二选一：

1. 环境变量 `T8T_PASSWORD`
2. 环境变量 `T8T_ACCOUNTS_MODULE` 指向本机模块，模块提供 `get_password(phone)`

密码放在哪，读 `grokbot/HANDOFF.md` 的「测试账号在哪」。本机探路账号模块只在本机引用，常见位置是 `/workspace/qa/t8t/multisite/thai-gray/lib/` 下的 accounts。不要把那个文件提交进仓库。

浏览器默认无头，直连，启动参数带 `--no-proxy-server`，不走 `127.0.0.1:8791`。要看窗口加 `--headed`。

证据默认写到 `/tmp/t8t-main-flow/`。脚本拒绝把证据写进本仓库。

本地检查判定函数：

```bash
python -m pytest grokbot/scripts/t8t/test_recall_verdict.py -q
```

CI 的回归工作流只跑 `tests/`，不会执行这些生产脚本。

## 断言依据

| 步骤 | 看到什么才算数 | 依据 | 没有正式编号时 |
| --- | --- | --- | --- |
| 登录 | 清会话后重新登录，离开登录页，账号页同时有会员名、UID、可用余额。请求是 `POST /auth/playerLogin` | 派单安全路径 | 信号符合记待确认 |
| 底栏 | Home、Promotion、Agent、Account 的高亮和正文都要对上，不能只看 URL | 派单安全路径 | 正文字样没有用例编号。信号符合记待确认；高亮对、正文没有这些词，也记待确认 |
| 进 Win Go | 玩法画面里要有倒计时、玩法说明、期号或 Win Go 档位。不点数字、颜色、GET STARTED | MSK-3 | 画面出现可以记通过。只有 HTTP 200 或 URL 变化记未验证 |
| 回收 | 用当前登录会话自己的 `withdrawAllVendor`。记录回收前后的可用余额、保险箱、进入前的游戏钱包，以及 HTTP 状态和外层 code | 用户回收规则 | 游戏钱包大于 0，回收后主钱包没有增加：失败待核。余额没读全，或只看到 200：待确认 |
| 换厂商 | 回收判定为通过之后才做。先关弹窗，再点接近正方形的游戏卡片，不点赔率或标题 | 派单安全路径 | 弹窗没关或没有 `enterGame`：未验证或阻塞。发出了请求也不写成通过 |

进游戏时两个钱包数字不同，本身不判失败。回收后主钱包仍不增加，不能再用「两个钱包本来分开」解释成通过。

## 退出码

| 码 | 含义 |
| --- | --- |
| 0 | 已执行的检查都是通过，或只是按规则未测 |
| 1 | 失败 |
| 2 | 没有密码 |
| 3 | 阻塞或未验证 |
| 4 | 跳过。打不开、地区或 IP 不支持、维护 |
| 5 | 待确认。登录和底栏信号符合也走这里 |
| 6 | 失败待核。回收后主钱包没有按规则增加 |

多个结论同时出现时，按 1、6、3、5、4 的顺序取第一个。

## 故意不做

不下注，不充值，不提现，不领取，不注册，不改资料，不进生产后台，不重放别人的 token。不点 Receive、Participate、SPIN、Install、Detail、Deposit Now、GET STARTED、数字或颜色。

不覆盖活动详情、记录、客服、邮箱登录提交，以及 Win Go 和一次 Aviator 卡片尝试以外的厂商。短信或邮箱验证码出现时，这一步会停在未验证，脚本不代填。
