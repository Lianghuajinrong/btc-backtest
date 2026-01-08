# Vercel 部署指南

## 快速部署步骤

### 1. 访问 Vercel
访问：https://vercel.com

### 2. 登录
- 点击右上角 "Sign Up" 或 "Login"
- 选择 "Continue with GitHub"
- 授权 Vercel 访问你的 GitHub 账号

### 3. 导入项目
- 点击 "Add New Project"
- 在仓库列表中找到 `Lianghuajinrong/btc-backtest`
- 点击 "Import"

### 4. 配置项目
- Framework Preset: 选择 **"Other"** 或 **"Vite"**（如果没有Other选项）
- Root Directory: 留空（默认）
- Build Command: 留空（前端是静态文件，不需要构建）
- Output Directory: 留空
- Install Command: 留空

### 5. 环境变量（可选）
如果需要，可以添加环境变量：
- `API_BASE_URL`: 你的 Railway 后端 URL

### 6. 部署
- 点击 "Deploy"
- 等待 1-2 分钟
- 部署完成后会显示前端 URL（例如：`https://btc-backtest.vercel.app`）

### 7. 完成！
现在你可以访问前端 URL，使用在线版本的回测系统了！

---

## 常见问题

**Q: 前端无法连接到后端？**
A: 确保 `index.html` 中的 API_BASE 已更新为正确的 Railway URL。

**Q: CORS 错误？**
A: 后端已经配置了 CORS，允许所有来源。如果仍有问题，检查后端日志。

**Q: 如何更新代码？**
A: 每次推送到 GitHub，Vercel 会自动重新部署。
