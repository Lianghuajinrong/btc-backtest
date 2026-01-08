# Railway 部署指南

## 快速部署步骤

### 1. 访问 Railway
访问：https://railway.app

### 2. 登录
- 点击右上角 "Login"
- 选择 "Login with GitHub"
- 授权 Railway 访问你的 GitHub 账号

### 3. 创建新项目
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 在仓库列表中找到 `Lianghuajinrong/btc-backtest`
- 点击选择

### 4. 等待部署
- Railway 会自动检测到 `requirements.txt` 和 `backend.py`
- 等待 2-3 分钟，看到 "Deploy successful" 表示成功

### 5. 获取域名
- 点击项目卡片进入项目详情
- 点击 "Settings" 标签
- 找到 "Domains" 部分
- 如果没有域名，点击 "Generate Domain"
- 复制生成的 URL（例如：`https://btc-backtest-production.up.railway.app`）

### 6. 告诉我你的 Railway URL
把获取到的完整 URL 发给我，我会更新前端代码。

---

## 常见问题

**Q: Railway 找不到我的仓库？**
A: 确保已经授权 Railway 访问 GitHub，并且仓库是公开的或你已经授权了私有仓库访问。

**Q: 部署失败？**
A: 查看 Railway 的 "Deployments" 标签中的日志，把错误信息发给我。

**Q: 如何查看日志？**
A: 在项目页面点击 "Deployments" → 选择最新的部署 → 查看日志。
