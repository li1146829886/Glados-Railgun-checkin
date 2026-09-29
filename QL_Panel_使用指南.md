# GLaDOS 签到 · 青龙面板使用指南

## 📁 文件清单

把以下文件放到青龙服务器同一个目录下（例如 `/ql/data/scripts/glados/`）：

| 文件                  | 作用                                  |
| ------------------- | ----------------------------------- |
| `checkin.py`        | 签到主脚本（原项目文件，**不要改**）                |
| `run_and_notify.py` | 包装脚本：运行 checkin.py + 把完整日志推送到 QQ 邮箱 |
| `logging_config.py` | checkin.py 依赖的日志配置                  |

## ⚙️ 安装依赖

青龙面板 → 依赖管理 → 新建依赖：

| 名称           | 类型      |
| ------------ | ------- |
| `requests`   | Python3 |
| `pypushdeer` | Python3 |

> `run_and_notify.py` 本身只用到 Python 标准库，不需要额外装包。

## 🔑 配置环境变量

青龙面板 → 环境变量 → 新建：

| 变量名                    | 必须     | 说明                                       | 示例                          |
| ---------------------- | ------ | ---------------------------------------- | --------------------------- |
| `GLADOS_COOKIES`       | ✅      | 签到 Cookie，多账号用 `&` 分隔                    | `koa:sess=xxx&koa:sess=yyy` |
| `EMAIL_USER`           | 邮件推送必配 | QQ 邮箱完整地址（既是发件也是收件）                      | `123456@qq.com`             |
| `EMAIL_PASSWORD`       | 邮件推送必配 | QQ 邮箱 **SMTP 授权码**（16 位，不是登录密码）          | —                           |
| `PUSHDEER_SENDKEY`     | ❌ 可选   | PushDeer 手机推送 key                        | —                           |
| `GLADOS_EXCHANGE_PLAN` | ❌ 可选   | 自动兑换策略：`plan100` / `plan200` / `plan500` | —                           |
| `GLADOS_VERBOSE`       | ❌ 可选   | 详细日志：`true` / `false`（默认 false）          | —                           |

### SMTP 授权码获取

登录 QQ 邮箱网页版 → **设置** → **账户** → 往下滚找到「POP3/SMTP/IMAP」→ 开启「SMTP 服务」→ 按提示发短信验证 → 验证通过后会显示 **16 位授权码**。

## ⏰ 添加定时任务

青龙面板 → 定时任务 → 新建任务：

| 字段    | 填写                                |
| ----- | --------------------------------- |
| 任务名称  | `GLaDOS 签到`                       |
| 命令/脚本 | 填 `run_and_notify.py` 的**完整绝对路径** |
| 定时规则  | 按需设置，例如 `0 30 8 * * ?`（每天 08:30）  |

> 注意：脚本路径要指向 `run_and_notify.py`，**不是** `checkin.py`！

**示例路径**：

```
/ql/data/scripts/glados/run_and_notify.py
```

## 📧 邮件效果

```
主题: GLaDOS 签到 成功 - 2026-09-29
内容:
时间：2026-09-29 10:21:27
退出码：0

--- checkin.py 输出 ---
🚀 步骤 1: 加载配置
🚀 步骤 2: 执行签到
...（完整签到日志）
🏁========== 签到总结 ==========
GLaDOS 签到, 成功0, 失败2, 重复2
[run_and_notify] 邮件已推送到 123456@qq.com
```

## 🔍 运行验证

手动点定时任务的「运行」按钮，等 10\~15 秒，看日志末尾：

```
[run_and_notify] 邮件已推送到 xxx@qq.com    ← ✅ 成功
[run_and_notify] 邮件发送失败: ...           ← ❌ 失败，看错误信息排查
EMAIL_USER / EMAIL_PASSWORD 未设置            ← ❌ 环境变量没配
```

然后检查 QQ 邮箱收件箱（没收到记得查**垃圾邮件**）。

## 🩹 常见问题

| 现象                                          | 说明 / 处理                                           |
| ------------------------------------------- | ------------------------------------------------- |
| 日志全是 checkin.py 输出，没有 `[run_and_notify]` 前缀 | 定时任务脚本路径错了，还是跑的 checkin.py，改成 run\_and\_notify.py |
| `EMAIL_USER / EMAIL_PASSWORD 未设置`           | 青龙环境变量没配或名字写错                                     |
| `name 'smtplib' is not defined`             | run\_and\_notify.py 版本过旧，更新到最新版                   |
| `500 authentication failed` 或 `535`         | SMTP 授权码错了，去 QQ 邮箱重新生成 16 位                       |
| `The "From" header is missing or invalid`   | run\_and\_notify.py 版本过旧，更新（已用 formataddr 修复）     |
| `railgun.info` 全部 `No permission`           | 该域名可能已失效，不影响 glados.cloud 签到                      |
| 邮件没收到                                       | 查垃圾邮件；QQ 邮箱偶尔延迟 1-2 分钟；青龙也会自动把日志推到你全局配置的渠道，可能收到重复 |

