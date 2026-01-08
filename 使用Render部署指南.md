# 🚀 使用Render部署后端指南

## 问题说明
Railway账户是"有限套餐"，只能部署数据库，无法部署应用服务。

## 解决方案：使用Render（免费）

Render提供免费套餐，可以部署Python应用，非常适合我们的项目！

---

## 📦 第一步：部署后端到Render

### 1. 访问Render
访问：https://render.com

### 2. 注册/登录
- 点击右上角 "Sign Up" 或 "Get Started"
- 选择 "Continue with GitHub"
- 授权Render访问你的GitHub账号

### 3. 创建新Web服务
- 登录后，点击 "New +" 按钮
- 选择 "Web Service"

### 4. 连接GitHub仓库
- 点击 "Connect GitHub"
- 如果还没连接，点击 "Configure GitHub App"
- 授权Render访问你的仓库
- 选择仓库：`Lianghuajinrong/btc-backtest`

### 5. 配置服务
填写以下信息：

**基本信息：**
- **Name**: `btc-backtest-api`（或任意名称）
- **Region**: 选择离你最近的区域（如 `Singapore` 或 `Oregon (US West)`）
- **Branch**: `main`
- **Root Directory**: `10000`（重要！因为文件在10000目录下）

**构建和启动：**
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn backend:app --host 0.0.0.0 --port $PORT`

**计划：**
- **Plan**: 选择 **Free**（免费套餐）

### 6. 高级设置（可选）
点击 "Advanced" 可以设置：
- **Environment Variables**: 暂时不需要
- **Health Check Path**: `/` 或 `/docs`（FastAPI文档）

### 7. 部署
- 点击 "Create Web Service"
- 等待部署完成（约3-5分钟）
- 部署完成后，Render会生成一个URL（例如：`https://btc-backtest-api.onrender.com`）

### 8. 获取后端URL
- 部署完成后，在服务页面顶部会显示URL
- **复制这个URL**，发给我，我会更新前端代码

---

## ⚠️ 重要提示

### Render免费套餐限制：
- 服务在15分钟无活动后会进入休眠状态
- 首次访问休眠服务需要等待30-60秒唤醒
- 每月有使用时间限制（通常足够个人项目使用）

### 如果服务休眠：
- 这是正常的，首次访问会唤醒
- 或者可以升级到付费套餐（$7/月起）避免休眠

---

## ✅ 完成后的下一步

获取到Render的URL后，告诉我，我会：
1. 更新 `index.html` 中的API地址
2. 提交更改到GitHub
3. 然后帮你部署前端到Vercel

---

## 💡 替代方案

如果不想使用Render，也可以考虑：
- **Fly.io**：也有免费套餐
- **Heroku**：需要信用卡，但有免费额度
- **升级Railway套餐**：$5/月起

但Render是最简单、最快速的免费选择！
