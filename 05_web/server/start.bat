@echo off
chcp 65001 >nul
cd /d "%~dp0"
if "%~1"=="" (
    echo [演示模式] 浏览器打开 http://127.0.0.1:8000
    python app.py --demo
) else (
    echo [串口模式] %1  浏览器打开 http://127.0.0.1:8000
    python app.py %*
)
pause
