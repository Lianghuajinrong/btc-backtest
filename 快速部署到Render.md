# 🚀 快速部署到Render（5分钟）

## ✅ 已准备好的配置
我已经更新了 `render.yaml` 文件，配置已经准备好了！

---

## 📋 部署步骤

### 1. 访问Render
打开：https://render.com

### 2. 登录
- 点击 "Sign Up" 或 "Get Started"
- 选择 "Continue with GitHub"
- 授权Render访问GitHub

### 3. 创建Web服务
- 点击 "New +" → "Web Service"
- 点击 "Connect GitHub"（如果还没连接）
- 选择仓库：`Lianghuajinrong/btc-backtest`

### 4. 配置（重要！）

**基本信息：**
- Name: `btc-backtest-api`
- Region: `Singapore` 或 `Oregon`
- Branch: `main`
- **Root Directory**: `10000` ⚠️ **这个很重要！**

**构建和启动：**
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn backend:app --host 0.0.0.0 --port $PORT`

**计划：**
- Plan: **Free**

### 5. 部署
- 点击 "Create Web Service"
- 等待3-5分钟
- 看到 "Live" 状态表示成功

### 6. 获取URL
- 部署完成后，页面顶部会显示URL
- 例如：`https://btc-backtest-api.onrender.com`
- **把这个URL发给我！**

---

## ⚡ 或者使用render.yaml自动部署

如果你看到 "Apply Render YAML" 选项：
1. 点击它
2. Render会自动读取 `render.yaml` 配置
3. 确认配置后点击部署

---

## 💡 提示

- Render免费套餐会在15分钟无活动后休眠
- 首次访问休眠服务需要等待30-60秒唤醒
- 这是正常的，不影响功能

---

## ✅ 完成后

把Render的URL发给我，我会：
1. 更新前端代码
2. 部署前端到Vercel
3. 完成整个项目部署！
