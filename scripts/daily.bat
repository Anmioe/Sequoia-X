@echo off
REM ============================================================
REM  Sequoia-X 每日选股一键运行
REM  步骤：1) 增量补当日 K 线（新浪源）  2) 跑策略 + 推飞书
REM  建议在交易日 15:00 收盘后运行
REM ============================================================
setlocal
set "ROOT=C:\Users\Administrator\WorkBuddy\2026-09-02-21-10-59\Sequoia-X"
set "LOG=%ROOT%\daily_%%date:~0,4%%%%date:~5,2%%%%date:~8,2%%.log"

cd /d "%ROOT%"
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] 虚拟环境不存在，请先运行环境准备 > "%LOG%"
    exit /b 1
)
call .venv\Scripts\activate.bat

echo [%date% %time%] === 1/2 增量补数据 === >> "%LOG%"
python scripts\backfill_sina.py >> "%LOG%" 2>&1

echo [%date% %time%] === 2/2 跑策略 + 推送 === >> "%LOG%"
python scripts\run_daily.py >> "%LOG%" 2>&1

echo [%date% %time%] === 完成 === >> "%LOG%"
endlocal
