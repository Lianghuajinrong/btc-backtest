# Gitee（码云）部署完整指南

## 📋 概述

本指南将帮助您将 BTC 回测项目部署到 Gitee（码云），包括：
- 代码仓库创建和推送
- 前端页面部署（Gitee Pages）
- 后端 API 部署方案

---

## 🎯 第一步：创建 Gitee 账户和仓库

### 1.1 注册/登录 Gitee

1. 访问：https://gitee.com
2. 如果没有账户，点击"注册"创建新账户
3. 如果已有账户，直接登录

### 1.2 创建新仓库

1. 登录后，点击右上角的 **"+"** 按钮
2. 选择 **"新建仓库"**
3. 填写仓库信息：
   - **仓库名称**：`btc-backtest`（或您喜欢的名称）
   - **仓库介绍**：`比特币双均线策略回测系统`
   - **可见性**：选择 **"公开"**（如果要用 Gitee Pages 免费部署）
   - **初始化仓库**：
     - ✅ 勾选 "使用 Readme 文件初始化这个仓库"（可选）
     - ❌ 不勾选其他选项（我们已有代码）
4. 点击 **"创建"**

### 1.3 获取仓库地址

创建成功后，您会看到仓库页面，记录以下信息：
- **HTTPS 地址**：`https://gitee.com/您的用户名/btc-backtest.git`
- **SSH 地址**：`git@gitee.com:您的用户名/btc-backtest.git`

---

## 🔧 第二步：配置本地 Git 并推送代码

### 2.1 添加 Gitee 远程仓库

在项目目录打开 PowerShell，执行以下命令：

```powershell
# 切换到项目目录
cd "c:\Users\范子阳\Desktop\10000"

# 添加 Gitee 远程仓库（替换为您的实际地址）
git remote add gitee https://gitee.com/您的用户名/btc-backtest.git

# 或者使用 SSH（如果已配置 SSH 密钥）
# git remote add gitee git@gitee.com:您的用户名/btc-backtest.git

# 查看所有远程仓库
git remote -v
```

**预期输出**：
```
gitee   https://gitee.com/您的用户名/btc-backtest.git (fetch)
gitee   https://gitee.com/您的用户名/btc-backtest.git (push)
origin  https://github.com/Lianghuajinrong/btc-backtest.git (fetch)
origin  https://github.com/Lianghuajinrong/btc-backtest.git (push)
```

### 2.2 添加所有文件到 Git

```powershell
# 添加所有文件
git add .

# 检查状态
git status
```

### 2.3 提交更改

```powershell
# 提交所有更改
git commit -m "初始提交：BTC回测系统完整代码，包含修复后的backend.py"
```

### 2.4 推送到 Gitee

```powershell
# 推送到 Gitee（首次推送）
git push -u gitee main

# 如果 main 分支不存在，可能需要先创建
# git push -u gitee main:main
```

**如果推送成功**：
- 会看到类似 "Writing objects: 100%..." 的输出
- 代码已推送到 Gitee

**如果推送失败 - 认证问题**：
- Gitee 需要身份验证
- 参考下面的"Gitee 认证配置"部分

---

## 🔐 第三步：Gitee 认证配置

### 方案 A：使用 HTTPS + 个人访问令牌（推荐）

1. **生成个人访问令牌**：
   - 登录 Gitee
   - 点击右上角头像 → **"设置"**
   - 左侧菜单选择 **"安全设置"** → **"私人令牌"**
   - 点击 **"生成新令牌"**
   - 填写描述：`本地开发推送`
   - 勾选权限：`projects`（项目权限）
   - 点击 **"提交"**
   - **重要**：复制生成的令牌（只显示一次）

2. **使用令牌推送**：
   ```powershell
   # 推送时会提示输入用户名和密码
   # 用户名：您的 Gitee 用户名
   # 密码：使用刚才生成的个人访问令牌（不是账户密码）
   git push -u gitee main
   ```

3. **保存凭据（可选）**：
   ```powershell
   # Windows 会提示保存凭据，选择"是"
   # 或者手动配置
   git config --global credential.helper wincred
   ```

### 方案 B：使用 SSH 密钥（更安全）

1. **生成 SSH 密钥**（如果还没有）：
   ```powershell
   # 生成 SSH 密钥
   ssh-keygen -t rsa -C "您的邮箱@example.com"
   # 按 Enter 使用默认路径
   # 设置密码（可选）
   ```

2. **复制公钥**：
   ```powershell
   # 查看公钥内容
   cat ~/.ssh/id_rsa.pub
   # 复制输出的内容
   ```

3. **添加到 Gitee**：
   - 登录 Gitee
   - 点击右上角头像 → **"设置"**
   - 左侧菜单选择 **"SSH公钥"**
   - 点击 **"添加公钥"**
   - 粘贴刚才复制的公钥
   - 填写标题：`我的电脑`
   - 点击 **"确定"**

4. **测试连接**：
   ```powershell
   ssh -T git@gitee.com
   # 应该看到：Hi 您的用户名! You've successfully authenticated...
   ```

5. **修改远程地址为 SSH**：
   ```powershell
   # 删除 HTTPS 远程地址
   git remote remove gitee
   
   # 添加 SSH 远程地址
   git remote add gitee git@gitee.com:您的用户名/btc-backtest.git
   
   # 推送
   git push -u gitee main
   ```

---

## 🌐 第四步：部署前端页面（Gitee Pages）

### 4.1 准备前端文件

确保 `index.html` 文件在项目根目录或指定目录中。

### 4.2 配置 Gitee Pages

1. **进入仓库设置**：
   - 在 Gitee 仓库页面，点击 **"服务"** 标签
   - 选择 **"Gitee Pages"**

2. **配置 Pages**：
   - **部署分支**：选择 `main`（或 `master`）
   - **部署目录**：
     - 如果 `index.html` 在根目录：选择 `/`（根目录）
     - 如果 `index.html` 在 `10000` 目录：选择 `/10000`
   - 点击 **"启动"**

3. **等待部署**：
   - 部署通常需要 1-3 分钟
   - 部署成功后，会显示访问地址：
     - `https://您的用户名.gitee.io/btc-backtest/`
     - 或 `https://您的用户名.gitee.io/btc-backtest/10000/`（如果部署目录是 `/10000`）

### 4.3 更新前端 API 地址

由于后端可能部署在不同的地址，需要更新 `index.html` 中的 API 地址：

1. **打开 `index.html`**
2. **查找 API 地址配置**（通常在 JavaScript 部分）
3. **更新为新的后端地址**：
   ```javascript
   // 示例：如果后端部署在某个服务器上
   const API_BASE_URL = 'https://您的后端地址.com';
   // 或者使用相对路径（如果前后端在同一域名下）
   const API_BASE_URL = '/api';
   ```

4. **提交并推送更改**：
   ```powershell
   git add index.html
   git commit -m "更新前端API地址"
   git push gitee main
   ```

5. **重新部署 Pages**：
   - 在 Gitee Pages 页面点击 **"更新"** 按钮

---

## 🚀 第五步：后端 API 部署方案

Gitee 本身不提供后端服务托管，您需要选择以下方案之一：

### 方案 A：使用 Gitee Go（CI/CD 自动部署）

1. **启用 Gitee Go**：
   - 在仓库页面，点击 **"服务"** → **"Gitee Go"**
   - 点击 **"启用"**

2. **创建部署脚本**：
   创建 `.gitee-ci.yml` 文件：
   ```yaml
   version: '1.0'
   stages:
     - deploy
   deploy:
     stage: deploy
     script:
       - echo "部署后端到服务器"
       # 添加您的部署命令
   ```

### 方案 B：使用第三方云服务（推荐）

#### B1. 使用 Render（如果网络允许）

1. **连接 Gitee 仓库**：
   - 登录 Render：https://render.com
   - 创建新的 Web Service
   - 连接 Gitee 仓库
   - 选择仓库和分支

2. **配置部署**：
   - **Build Command**：`pip install -r requirements.txt`
   - **Start Command**：`python backend.py`
   - **Environment**：Python 3

#### B2. 使用 Railway

1. **连接 Gitee**：
   - 登录 Railway：https://railway.app
   - 创建新项目
   - 选择 "Deploy from Git repo"
   - 连接 Gitee 账户和仓库

2. **配置部署**：
   - Railway 会自动检测 Python 项目
   - 确保 `Procfile` 或 `railway.json` 配置正确

#### B3. 使用国内云服务

- **阿里云**：https://www.aliyun.com
- **腾讯云**：https://cloud.tencent.com
- **华为云**：https://www.huaweicloud.com

这些服务通常提供：
- 云服务器（ECS）
- 容器服务
- Serverless 函数

### 方案 C：本地服务器部署

如果您有自己的服务器：

1. **SSH 连接到服务器**
2. **克隆仓库**：
   ```bash
   git clone https://gitee.com/您的用户名/btc-backtest.git
   cd btc-backtest
   ```

3. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

4. **运行后端**：
   ```bash
   python backend.py
   ```

5. **使用进程管理器**（如 PM2 或 supervisor）：
   ```bash
   # 使用 PM2（需要先安装 Node.js）
   npm install -g pm2
   pm2 start backend.py --interpreter python3
   pm2 save
   pm2 startup
   ```

---

## 📝 第六步：更新前端 API 地址

部署后端后，需要更新前端的 API 地址：

### 6.1 查找 API 配置

打开 `index.html`，查找类似以下代码：

```javascript
// 查找 API 基础地址
const API_BASE_URL = 'https://btc-backtest.onrender.com';
// 或
const API_BASE_URL = 'http://localhost:8000';
```

### 6.2 更新为新的后端地址

```javascript
// 替换为您的实际后端地址
const API_BASE_URL = 'https://您的后端地址.com';
```

### 6.3 提交并推送

```powershell
git add index.html
git commit -m "更新前端API地址为新的后端服务"
git push gitee main
```

### 6.4 重新部署 Pages

在 Gitee Pages 页面点击 **"更新"** 按钮。

---

## ✅ 第七步：验证部署

### 7.1 验证前端

1. **访问 Gitee Pages 地址**：
   - `https://您的用户名.gitee.io/btc-backtest/`
   - 检查页面是否正常加载

2. **测试功能**：
   - 输入参数（短均线、长均线、初始资金）
   - 点击"运行回测"
   - 检查是否能正常获取数据并显示图表

### 7.2 验证后端

1. **测试 API 端点**：
   ```bash
   # 测试数据接口
   curl https://您的后端地址.com/api/btc_daily
   
   # 测试回测接口
   curl "https://您的后端地址.com/api/backtest/double_ma?short=10&long=50"
   ```

2. **检查 API 文档**：
   - 访问：`https://您的后端地址.com/docs`
   - 应该能看到 FastAPI 自动生成的 API 文档

---

## 🔄 日常更新流程

### 更新代码并推送

```powershell
# 1. 修改代码
# ... 编辑文件 ...

# 2. 添加更改
git add .

# 3. 提交
git commit -m "更新说明"

# 4. 推送到 Gitee
git push gitee main

# 5. 如果前端有更改，更新 Gitee Pages
# 在 Gitee Pages 页面点击"更新"
```

---

## 🐛 常见问题排查

### 问题 1：推送失败 - 认证错误

**解决方案**：
- 检查个人访问令牌是否正确
- 确认用户名和令牌匹配
- 尝试重新生成令牌

### 问题 2：Gitee Pages 无法访问

**解决方案**：
- 检查部署目录是否正确
- 确认 `index.html` 在指定目录中
- 检查仓库是否为公开仓库（私有仓库需要付费）

### 问题 3：前端无法连接后端

**解决方案**：
- 检查 CORS 配置（后端已配置允许所有来源）
- 确认后端地址正确
- 检查浏览器控制台错误信息
- 确认后端服务正在运行

### 问题 4：后端部署失败

**解决方案**：
- 检查 `requirements.txt` 是否包含所有依赖
- 确认 Python 版本正确（`runtime.txt`）
- 检查 `Procfile` 或启动命令是否正确
- 查看部署日志中的错误信息

---

## 📌 重要文件清单

确保以下文件已提交到 Gitee：

- ✅ `backend.py` - 后端主文件（已修复编码问题）
- ✅ `index.html` - 前端页面
- ✅ `requirements.txt` - Python 依赖
- ✅ `runtime.txt` - Python 版本（如需要）
- ✅ `Procfile` - 进程配置文件（如需要）
- ✅ `btc_data_local.py` - 本地数据生成器
- ✅ `.gitignore` - Git 忽略文件

---

## 🎉 完成检查清单

- [ ] Gitee 账户已创建/登录
- [ ] 仓库已创建
- [ ] 代码已推送到 Gitee
- [ ] Gitee Pages 已配置并部署
- [ ] 前端页面可以正常访问
- [ ] 后端 API 已部署
- [ ] 前端 API 地址已更新
- [ ] 前后端可以正常通信
- [ ] 回测功能测试通过

---

## 📞 需要帮助？

如果遇到问题：

1. **查看 Gitee 文档**：https://gitee.com/help
2. **检查部署日志**：在 Gitee Pages 或部署服务中查看
3. **查看浏览器控制台**：F12 打开开发者工具
4. **检查网络连接**：确认可以访问 Gitee 和部署的服务

---

**最后更新**：2026年1月8日  
**状态**：等待部署到 Gitee
