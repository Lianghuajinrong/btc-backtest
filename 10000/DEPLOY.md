# 部署指南

本项目包含前端（HTML）和后端（Python FastAPI），需要分别部署。

## 方案一：Vercel（前端）+ Railway（后端）推荐 ⭐

### 1. 部署后端到 Railway

1. **注册 Railway 账号**
   - 访问 https://railway.app
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库

3. **配置环境变量**
   - Railway 会自动检测到 `requirements.txt` 和 `backend.py`
   - 确保端口设置为环境变量 `PORT`（Railway 会自动提供）

4. **修改 backend.py 的启动方式**
   ```python
   # 在 backend.py 最后添加：
   if __name__ == "__main__":
       import uvicorn
       import os
       port = int(os.environ.get("PORT", 8000))
       uvicorn.run("backend:app", host="0.0.0.0", port=port, reload=False)
   ```

5. **获取后端URL**
   - Railway 会提供一个类似 `https://your-app-name.up.railway.app` 的URL
   - 复制这个URL

### 2. 部署前端到 Vercel

1. **注册 Vercel 账号**
   - 访问 https://vercel.com
   - 使用 GitHub 账号登录

2. **导入项目**
   - 点击 "Add New Project"
   - 选择你的 GitHub 仓库
   - Framework Preset 选择 "Other"

3. **修改前端 API 地址**
   - 在 `index.html` 中，将 `window.API_BASE_URL` 替换为你的 Railway 后端URL
   - 或者创建环境变量（需要修改代码支持）

4. **部署**
   - 点击 "Deploy"
   - Vercel 会自动部署并提供一个URL

## 方案二：Vercel（前端）+ Render（后端）

### 1. 部署后端到 Render

1. **注册 Render 账号**
   - 访问 https://render.com
   - 使用 GitHub 账号登录

2. **创建 Web Service**
   - 点击 "New" → "Web Service"
   - 连接你的 GitHub 仓库
   - 设置：
     - Name: `btc-backtest-api`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `python backend.py`
     - Plan: Free

3. **环境变量**
   - 添加 `PORT=8000`（Render 会自动提供 PORT 环境变量）

4. **获取后端URL**
   - Render 会提供一个类似 `https://your-app-name.onrender.com` 的URL

### 2. 部署前端到 Vercel
   - 同方案一的步骤2

## 方案三：全部部署到 Vercel（Serverless Functions）

需要将后端改为 Vercel Serverless Functions 格式，比较复杂，不推荐。

## 快速部署步骤（Railway + Vercel）

### 后端（Railway）

1. 推送代码到 GitHub
2. 在 Railway 中导入项目
3. 等待部署完成
4. 复制部署URL（例如：`https://btc-backtest.up.railway.app`）

### 前端（Vercel）

1. 修改 `index.html` 中的 API_BASE：
   ```javascript
   const API_BASE = 
     window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
       ? "http://127.0.0.1:8000"
       : "https://btc-backtest.up.railway.app";  // 替换为你的Railway URL
   ```

2. 推送代码到 GitHub
3. 在 Vercel 中导入项目
4. 部署完成

## 注意事项

1. **CORS 配置**：后端已经配置了 CORS，允许所有来源访问
2. **环境变量**：生产环境可能需要设置环境变量
3. **数据缓存**：后端使用 `@lru_cache`，重启后会清除缓存
4. **免费额度**：Railway 和 Render 都有免费额度限制，注意使用量

## 测试部署

部署完成后：
1. 访问前端URL
2. 打开浏览器开发者工具（F12）
3. 查看 Network 标签，确认API请求是否成功
4. 如果出现CORS错误，检查后端CORS配置

## 故障排查

- **502 Bad Gateway**：后端未启动或崩溃
- **CORS 错误**：检查后端 CORS 配置
- **404 Not Found**：检查 API 路径是否正确
- **超时**：免费服务可能有冷启动延迟
