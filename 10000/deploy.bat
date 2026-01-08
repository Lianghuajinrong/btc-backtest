@echo off
chcp 65001 >nul
echo 🚀 开始部署流程...
echo.

REM 检查是否已初始化 git
if not exist ".git" (
    echo 📦 初始化 Git 仓库...
    git init
    git add .
    git commit -m "Initial commit: BTC双均线回测系统"
    echo ✅ Git 仓库已初始化
    echo.
)

REM 检查是否有远程仓库
git remote | findstr /C:"origin" >nul
if errorlevel 1 (
    echo ⚠️  未检测到远程仓库，请先创建 GitHub 仓库：
    echo    1. 访问 https://github.com/new
    echo    2. 创建新仓库（例如：btc-backtest）
    echo    3. 复制仓库 URL
    echo    4. 运行: git remote add origin ^<你的仓库URL^>
    echo.
    set /p has_repo="是否已创建 GitHub 仓库？(y/n): "
    if /i not "%has_repo%"=="y" (
        echo 请先创建 GitHub 仓库，然后重新运行此脚本
        pause
        exit /b 1
    )
    set /p repo_url="请输入你的 GitHub 仓库 URL: "
    git remote add origin "%repo_url%"
    echo ✅ 已添加远程仓库
    echo.
)

REM 推送代码
echo 📤 推送代码到 GitHub...
git add .
git commit -m "准备部署: 添加部署配置文件" 2>nul || echo 没有新更改
git push -u origin main 2>nul || git push -u origin master
echo ✅ 代码已推送到 GitHub
echo.

echo ✅ 代码准备完成！
echo.
echo 📋 下一步操作：
echo.
echo 1️⃣  部署后端到 Railway:
echo    - 访问 https://railway.app
echo    - 使用 GitHub 登录
echo    - 点击 'New Project' → 'Deploy from GitHub repo'
echo    - 选择你的仓库
echo    - 等待部署完成，复制后端 URL
echo.
echo 2️⃣  更新前端 API 地址:
echo    - 编辑 index.html 第 243 行
echo    - 将 Railway URL 替换为你的后端地址
echo    - 提交并推送: git add index.html ^&^& git commit -m "Update API URL" ^&^& git push
echo.
echo 3️⃣  部署前端到 Vercel:
echo    - 访问 https://vercel.com
echo    - 使用 GitHub 登录
echo    - 点击 'Add New Project'
echo    - 选择你的仓库
echo    - Framework Preset 选择 'Other'
echo    - 点击 'Deploy'
echo.
echo 🎉 完成！
pause
