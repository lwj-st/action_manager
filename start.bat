@echo off
chcp 65001 >nul
title GitHub Action 管理系统

echo ========================================
echo    GitHub Action 管理系统
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境
    echo 请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo Python环境检查通过
echo.

echo 正在检查依赖包...
python -c "import PyQt5, requests" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖包安装失败
        pause
        exit /b 1
    )
)

echo 依赖包检查通过
echo.

echo 启动GitHub Action管理系统...
python main.py

if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
) 