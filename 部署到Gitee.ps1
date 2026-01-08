# Gitee 部署脚本
# 使用方法：在 PowerShell 中执行：.\部署到Gitee.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BTC回测系统 - Gitee 部署脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在正确的目录
if (-not (Test-Path "backend.py")) {
    Write-Host "错误：未找到 backend.py 文件" -ForegroundColor Red
    Write-Host "请确保在项目根目录执行此脚本" -ForegroundColor Red
    exit 1
}

# 提示用户输入 Gitee 仓库地址
Write-Host "请输入您的 Gitee 仓库地址：" -ForegroundColor Yellow
Write-Host "示例：https://gitee.com/您的用户名/btc-backtest.git" -ForegroundColor Gray
$giteeUrl = Read-Host "Gitee 仓库地址"

if ([string]::IsNullOrWhiteSpace($giteeUrl)) {
    Write-Host "错误：仓库地址不能为空" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "开始部署流程..." -ForegroundColor Green
Write-Host ""

# 步骤 1：检查 Git 状态
Write-Host "[1/5] 检查 Git 状态..." -ForegroundColor Cyan
$gitStatus = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误：Git 未初始化或不在 Git 仓库中" -ForegroundColor Red
    exit 1
}

# 步骤 2：添加 Gitee 远程仓库
Write-Host "[2/5] 配置 Gitee 远程仓库..." -ForegroundColor Cyan
$existingRemote = git remote get-url gitee 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "检测到已存在的 gitee 远程仓库：$existingRemote" -ForegroundColor Yellow
    $update = Read-Host "是否更新为新的地址？(Y/N)"
    if ($update -eq "Y" -or $update -eq "y") {
        git remote set-url gitee $giteeUrl
        Write-Host "已更新 Gitee 远程仓库地址" -ForegroundColor Green
    }
} else {
    git remote add gitee $giteeUrl
    Write-Host "已添加 Gitee 远程仓库" -ForegroundColor Green
}

# 步骤 3：添加所有文件
Write-Host "[3/5] 添加文件到 Git..." -ForegroundColor Cyan
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告：git add 执行失败" -ForegroundColor Yellow
}

# 检查是否有未提交的更改
$status = git status --porcelain
if ($status) {
    Write-Host "检测到未提交的更改，需要提交" -ForegroundColor Yellow
    $commitMsg = Read-Host "请输入提交信息（直接回车使用默认信息）"
    if ([string]::IsNullOrWhiteSpace($commitMsg)) {
        $commitMsg = "部署到Gitee：更新代码"
    }
    git commit -m $commitMsg
    if ($LASTEXITCODE -ne 0) {
        Write-Host "警告：提交失败，但继续执行" -ForegroundColor Yellow
    } else {
        Write-Host "已提交更改" -ForegroundColor Green
    }
} else {
    Write-Host "没有未提交的更改" -ForegroundColor Green
}

# 步骤 4：推送到 Gitee
Write-Host "[4/5] 推送到 Gitee..." -ForegroundColor Cyan
Write-Host "提示：如果提示输入用户名和密码，" -ForegroundColor Yellow
Write-Host "      用户名：您的 Gitee 用户名" -ForegroundColor Yellow
Write-Host "      密码：使用个人访问令牌（不是账户密码）" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "确认推送？(Y/N)"
if ($confirm -eq "Y" -or $confirm -eq "y") {
    git push -u gitee main
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ 代码已成功推送到 Gitee！" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "✗ 推送失败" -ForegroundColor Red
        Write-Host "可能的原因：" -ForegroundColor Yellow
        Write-Host "1. 认证失败 - 请检查用户名和访问令牌" -ForegroundColor Yellow
        Write-Host "2. 网络问题 - 请检查网络连接" -ForegroundColor Yellow
        Write-Host "3. 分支名称不匹配 - 可能需要使用 master 而不是 main" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "请参考 'Gitee部署完整指南.md' 进行排查" -ForegroundColor Cyan
        exit 1
    }
} else {
    Write-Host "已取消推送" -ForegroundColor Yellow
    exit 0
}

# 步骤 5：显示后续步骤
Write-Host ""
Write-Host "[5/5] 部署完成！" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  后续步骤：" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 配置 Gitee Pages（部署前端）：" -ForegroundColor Yellow
Write-Host "   - 访问：$($giteeUrl -replace '\.git$', '')" -ForegroundColor Gray
Write-Host "   - 点击 '服务' → 'Gitee Pages'" -ForegroundColor Gray
Write-Host "   - 选择部署分支：main" -ForegroundColor Gray
Write-Host "   - 选择部署目录：/（如果 index.html 在根目录）" -ForegroundColor Gray
Write-Host "   - 或选择：/10000（如果 index.html 在 10000 目录）" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 部署后端 API：" -ForegroundColor Yellow
Write-Host "   - 参考 'Gitee部署完整指南.md' 中的后端部署方案" -ForegroundColor Gray
Write-Host "   - 推荐使用 Render、Railway 或国内云服务" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 更新前端 API 地址：" -ForegroundColor Yellow
Write-Host "   - 编辑 index.html，更新 API_BASE_URL" -ForegroundColor Gray
Write-Host "   - 重新推送到 Gitee" -ForegroundColor Gray
Write-Host "   - 在 Gitee Pages 页面点击 '更新'" -ForegroundColor Gray
Write-Host ""
Write-Host "详细说明请查看：Gitee部署完整指南.md" -ForegroundColor Cyan
Write-Host ""
