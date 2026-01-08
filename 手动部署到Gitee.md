# 手动部署到 Gitee - 简化版

## 📋 前置条件

1. ✅ 已创建 Gitee 账户
2. ✅ 已在 Gitee 创建仓库（仓库名：`btc-backtest`）
3. ✅ 已生成个人访问令牌（Gitee → 设置 → 安全设置 → 私人令牌）

---

## 🚀 执行步骤

### 第一步：添加 Gitee 远程仓库

在 PowerShell 中执行（**请替换为您的 Gitee 用户名**）：

```powershell
git remote add gitee https://gitee.com/您的用户名/btc-backtest.git
```

**验证是否添加成功**：
```powershell
git remote -v
```

应该看到两个远程仓库：
- `origin` → GitHub
- `gitee` → Gitee

---

### 第二步：添加所有文件并提交

```powershell
git add .
git commit -m "部署到Gitee：添加所有文件"
```

---

### 第三步：推送到 Gitee

```powershell
git push gitee main
```

**提示输入凭据时**：
- **用户名**：您的 Gitee 用户名
- **密码**：使用**个人访问令牌**（不是账户密码）

---

### 第四步：配置 Gitee Pages

1. 访问您的 Gitee 仓库页面
2. 点击 **"服务"** 标签
3. 选择 **"Gitee Pages"**
4. 配置：
   - 部署分支：`main`
   - 部署目录：`/`（根目录）
5. 点击 **"启动"**
6. 等待 1-3 分钟，获取访问地址

---

## ✅ 完成！

访问地址格式：`https://您的用户名.gitee.io/btc-backtest/`

---

## 🆘 常见问题

### Q1: 推送时提示认证失败
**A**: 确保使用个人访问令牌，不是账户密码

### Q2: 如何生成个人访问令牌？
**A**: Gitee → 右上角头像 → 设置 → 安全设置 → 私人令牌 → 生成新令牌

### Q3: 推送失败，提示仓库不存在
**A**: 确保已在 Gitee 创建了同名仓库

### Q4: Pages 无法访问
**A**: 确保仓库是**公开**的，私有仓库需要 Gitee 会员

---

## 📝 后续步骤

部署后端 API（参考 `Gitee部署完整指南.md`）
