# PowerShell脚本：推送代码到GitHub
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "推送代码到GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$repoUrl = "https://github.com/Lianghuajinrong/btc-backtest.git"

# 检查git是否安装
try {
    git --version | Out-Null
} catch {
    Write-Host "错误：Git未安装或不在PATH中" -ForegroundColor Red
    Write-Host "请访问 https://git-scm.com/download/win 安装Git" -ForegroundColor Yellow
    exit 1
}

# 初始化git（如果还没初始化）
if (-not (Test-Path .git)) {
    Write-Host "[1/5] 初始化Git仓库..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git仓库已初始化" -ForegroundColor Green
    Write-Host ""
}

# 添加所有文件
Write-Host "[2/5] 添加文件到Git..." -ForegroundColor Yellow
git add .
Write-Host "✓ 文件已添加" -ForegroundColor Green
Write-Host ""

# 提交
Write-Host "[3/5] 提交更改..." -ForegroundColor Yellow
git commit -m "Initial commit: BTC双均线回测系统" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 已提交" -ForegroundColor Green
} else {
    Write-Host "⚠ 提交失败（可能是没有更改）" -ForegroundColor Yellow
}
Write-Host ""

# 设置主分支
Write-Host "[4/5] 设置主分支..." -ForegroundColor Yellow
git branch -M main 2>&1 | Out-Null
Write-Host "✓ 主分支已设置" -ForegroundColor Green
Write-Host ""

# 检查并添加远程仓库
Write-Host "[5/5] 配置远程仓库..." -ForegroundColor Yellow
$remoteExists = git remote | Select-String -Pattern "origin"
if (-not $remoteExists) {
    git remote add origin $repoUrl
    Write-Host "✓ 远程仓库已添加: $repoUrl" -ForegroundColor Green
} else {
    git remote set-url origin $repoUrl
    Write-Host "✓ 远程仓库已更新: $repoUrl" -ForegroundColor Green
}
Write-Host ""

# 推送代码
Write-Host "正在推送到GitHub..." -ForegroundColor Yellow
Write-Host "注意：如果提示需要认证，请使用GitHub Personal Access Token" -ForegroundColor Cyan
Write-Host ""
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ 代码已成功推送到GitHub！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步：" -ForegroundColor Cyan
    Write-Host "1. 访问 https://railway.app 部署后端" -ForegroundColor White
    Write-Host "2. 获取Railway的URL后告诉我，我会更新前端代码" -ForegroundColor White
    Write-Host "3. 然后访问 https://vercel.com 部署前端" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "推送失败！可能的原因：" -ForegroundColor Red
    Write-Host "1. 需要GitHub认证（使用Personal Access Token）" -ForegroundColor Yellow
    Write-Host "2. 网络连接问题" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "解决方案：" -ForegroundColor Cyan
    Write-Host "1. 访问 https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "2. 生成新的token（权限：repo）" -ForegroundColor White
    Write-Host "3. 使用token作为密码推送" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Red
}
