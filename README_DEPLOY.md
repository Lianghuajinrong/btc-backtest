# 🚀 快速部署指南

## 推荐方案：Vercel（前端）+ Railway（后端）

### 📋 前置准备

1. 将代码推送到 GitHub 仓库
2. 注册账号：
   - Railway: https://railway.app （免费）
   - Vercel: https://vercel.com （免费）

---

## 🔧 步骤一：部署后端到 Railway

### 1. 创建 Railway 项目

1. 访问 https://railway.app，使用 GitHub 登录
2. 点击 **"New Project"**
3. 选择 **"Deploy from GitHub repo"**
4. 选择你的仓库

### 2. 配置部署

Railway 会自动检测到：
- ✅ `requirements.txt`（Python 依赖）
- ✅ `backend.py`（启动文件）
- ✅ `Procfile`（启动命令）

### 3. 获取后端 URL

部署完成后，Railway 会提供一个 URL，例如：
```
https://btc-backtest-api.up.railway.app
```

**重要**：复制这个 URL，下一步会用到！

---

## 🎨 步骤二：部署前端到 Vercel

### 1. 修改前端 API 地址

在 `index.html` 第 239-242 行，将后端 URL 替换为你的 Railway URL：

```javascript
const API_BASE = 
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? "http://127.0.0.1:8000"  // 本地开发
    : "https://btc-backtest-api.up.railway.app";  // ⬅️ 替换为你的Railway URL
```

### 2. 提交代码

```bash
git add index.html
git commit -m "Update API URL for production"
git push
```

### 3. 部署到 Vercel

1. 访问 https://vercel.com，使用 GitHub 登录
2. 点击 **"Add New Project"**
3. 选择你的仓库
4. Framework Preset 选择 **"Other"**
5. 点击 **"Deploy"**

### 4. 获取前端 URL

Vercel 会提供一个 URL，例如：
```
https://btc-backtest.vercel.app
```

---

## ✅ 完成！

现在你可以：
1. 访问前端 URL 查看网页
2. 测试回测功能
3. 分享给其他人使用

---

## 🔍 故障排查

### 问题：前端显示 "回测失败"

**解决方案**：
1. 打开浏览器开发者工具（F12）
2. 查看 Console 和 Network 标签
3. 确认 API 请求是否成功
4. 检查后端 URL 是否正确

### 问题：CORS 错误

**解决方案**：
- 后端已经配置了 CORS，允许所有来源
- 如果仍有问题，检查后端日志

### 问题：502 Bad Gateway

**解决方案**：
- 后端可能崩溃了，查看 Railway 日志
- 检查 `requirements.txt` 是否完整
- 确认 Python 版本兼容

---

## 📝 其他部署选项

### Render（后端备选）

如果 Railway 不可用，可以使用 Render：

1. 访问 https://render.com
2. 创建 Web Service
3. 使用 `render.yaml` 配置文件
4. 获取 URL 并更新前端

### GitHub Pages（仅前端，不推荐）

GitHub Pages 只能部署静态文件，无法运行后端 API。

---

## 💡 提示

- **免费额度**：Railway 和 Vercel 都有免费额度，足够个人使用
- **自动部署**：每次推送到 GitHub，会自动重新部署
- **环境变量**：可以在 Railway/Vercel 中设置环境变量
- **日志查看**：在各自平台的控制台查看日志

---

## 🎉 享受你的在线回测系统！

如有问题，请查看 `DEPLOY.md` 获取更详细的说明。
