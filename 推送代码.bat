@echo off
chcp 65001 >nul
echo ========================================
echo 推送代码到GitHub
echo ========================================
echo.

REM 检查是否已初始化git
if not exist ".git" (
    echo [1/5] 初始化Git仓库...
    git init
    if errorlevel 1 (
        echo 错误：Git未安装或不在PATH中
        echo 请访问 https://git-scm.com/download/win 安装Git
        pause
        exit /b 1
    )
    echo ✓ Git仓库已初始化
    echo.
)

REM 添加所有文件
echo [2/5] 添加文件到Git...
git add .
if errorlevel 1 (
    echo 错误：添加文件失败
    pause
    exit /b 1
)
echo ✓ 文件已添加
echo.

REM 提交
echo [3/5] 提交更改...
git commit -m "Initial commit: BTC双均线回测系统"
if errorlevel 1 (
    echo 警告：提交失败（可能是没有更改）
)
echo ✓ 已提交
echo.

REM 设置主分支
echo [4/5] 设置主分支...
git branch -M main
echo ✓ 主分支已设置
echo.

REM 检查远程仓库
git remote | findstr /C:"origin" >nul
if errorlevel 1 (
    echo [5/5] 添加远程仓库...
    echo.
    echo 请输入你的GitHub仓库URL（例如：https://github.com/用户名/仓库名.git）
    set /p repo_url="仓库URL: "
    if "%repo_url%"=="" (
        echo 错误：未输入仓库URL
        pause
        exit /b 1
    )
    git remote add origin "%repo_url%"
    echo ✓ 远程仓库已添加
    echo.
) else (
    echo [5/5] 远程仓库已存在
    echo.
)

REM 推送代码
echo 正在推送到GitHub...
echo 注意：如果提示需要认证，请使用GitHub Personal Access Token
echo.
git push -u origin main
if errorlevel 1 (
    echo.
    echo ========================================
    echo 推送失败！可能的原因：
    echo 1. 需要GitHub认证（使用Personal Access Token）
    echo 2. 网络连接问题
    echo 3. 仓库URL不正确
    echo.
    echo 解决方案：
    echo 1. 访问 https://github.com/settings/tokens
    echo 2. 生成新的token（权限：repo）
    echo 3. 使用token作为密码推送
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 代码已成功推送到GitHub！
echo ========================================
echo.
echo 下一步：
echo 1. 访问 https://railway.app 部署后端
echo 2. 获取Railway的URL后告诉我，我会更新前端代码
echo 3. 然后访问 https://vercel.com 部署前端
echo.
pause
