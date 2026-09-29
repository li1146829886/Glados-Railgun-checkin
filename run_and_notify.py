#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立包装脚本：运行 checkin.py 后把完整日志推送到 QQ 邮箱。
不改原 checkin.py，青龙面板里把定时任务指向本脚本即可。

依赖：仅 Python 标准库（subprocess, smtplib, email, os, sys, datetime）。

环境变量：
  CHECKIN_PATH    checkin.py 的完整路径（选填，缺省自动取同目录下的 checkin.py）
  EMAIL_USER      QQ 邮箱完整地址（既是发件也是收件）
  EMAIL_PASSWORD  QQ 邮箱 SMTP 授权码（16 位，不是登录密码）
  其余 GLADOS_* / PUSHDEER_SENDKEY 透传给 checkin.py
"""

import datetime
import os
import smtplib
import subprocess
import sys

from email.mime.text import MIMEText
from email.utils import formataddr


def run_checkin() -> tuple[int, str, str]:
    """运行 checkin.py，返回 (退出码, stdout, stderr)。"""
    # 定位 checkin.py：优先用 CHECKIN_PATH 环境变量，否则取本脚本同目录下的 checkin.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    checkin_path = os.environ.get("CHECKIN_PATH", "").strip() or os.path.join(script_dir, "checkin.py")

    if not os.path.isfile(checkin_path):
        print(f"[run_and_notify] checkin.py 不存在: {checkin_path}")
        return 1, "", f"checkin.py 不存在: {checkin_path}"

    print(f"[run_and_notify] 执行: python {checkin_path}")
    result = subprocess.run(
        [sys.executable, checkin_path],
        capture_output=True,
        text=True,
        env=os.environ,  # 透传所有环境变量
    )
    return result.returncode, result.stdout or "", result.stderr or ""


def send_email(subject: str, body: str) -> bool:
    """通过 QQ 邮箱 SMTP_SSL(465) 发送邮件；EMAIL_USER / EMAIL_PASSWORD 缺一跳过。"""
    user = os.environ.get("EMAIL_USER", "").strip()
    password = os.environ.get("EMAIL_PASSWORD", "").strip()
    if not (user and password):
        print("[run_and_notify] EMAIL_USER / EMAIL_PASSWORD 未设置，跳过邮件推送。")
        return False
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = formataddr(("GLaDOS签到助手", user))
        msg["To"] = user
        msg["Subject"] = subject
        with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=15) as smtp:
            smtp.login(user, password)
            smtp.sendmail(user, [user], msg.as_string())
        print(f"[run_and_notify] 邮件已推送到 {user}")
        return True
    except Exception as e:
        print(f"[run_and_notify] 邮件发送失败: {e}")
        return False


def beijing_now_str() -> str:
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")


def main():
    # 1. 运行签到脚本
    rc, stdout, stderr = run_checkin()

    # 2. 合并日志（checkin.py 用 logging 写到 stderr 或 stdout 都要抓）
    log_text = f"时间：{beijing_now_str()}\n退出码：{rc}\n\n--- checkin.py 输出 ---\n"
    if stdout.strip():
        log_text += stdout
    if stderr.strip():
        log_text += ("\n\n--- stderr ---\n" if stdout.strip() else "") + stderr

    # 3. 打印到当前 stdout（青龙面板会捕获这份做运行日志）
    print(log_text)

    # 4. 推送邮件
    status_text = "成功" if rc == 0 else ("异常" if rc == 1 else f"失败(rc={rc})")
    subject = f"GLaDOS 签到 {status_text} - {beijing_now_str()[:10]}"
    send_email(subject, log_text)

    sys.exit(rc)


if __name__ == "__main__":
    main()
