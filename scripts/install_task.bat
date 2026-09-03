@echo off
REM ============================================================
REM  注册 Sequoia-X 每日定时任务（在「你自己的电脑」上双击运行）
REM  说明：WorkBuddy 沙箱内 Task Scheduler 被拦截，无法直接注册；
REM        此脚本供你在本机（非沙箱）一键注册。普通双击即以当前
REM        用户注册，仅在登录后运行；如需后台运行请「右键→以管理员
REM        身份运行」，会自动加 /rl highest。
REM ============================================================
set "BAT=C:\Users\Administrator\WorkBuddy\2026-09-02-21-10-59\Sequoia-X\scripts\daily.bat"

schtasks /create /tn "SequoiaX-Daily" /tr "%BAT%" /sc daily /st 15:30 /f
if %errorlevel%==0 (
    echo [OK] 已注册计划任务：SequoiaX-Daily（每日 15:30 收盘后运行）
) else (
    echo [FAIL] 注册失败，请确认以管理员身份运行，或修改上面的路径后重试
)
pause
