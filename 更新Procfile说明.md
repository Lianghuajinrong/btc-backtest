# 🔧 更新Procfile说明

## 问题
Railway显示服务器离线，可能是因为Procfile配置不正确。

## 解决方案
我已经更新了 `Procfile` 文件，使用标准的uvicorn启动命令。

## 需要你做的

### 方法1：通过GitHub网页更新（推荐）

1. **访问GitHub仓库**
   - 打开：https://github.com/Lianghuajinrong/btc-backtest

2. **编辑Procfile**
   - 点击 `Procfile` 文件
   - 点击右上角的 ✏️ "Edit" 按钮
   - 删除旧内容，粘贴以下内容：
   ```
   web: uvicorn backend:app --host 0.0.0.0 --port $PORT
   ```

3. **提交更改**
   - 在页面底部填写提交信息：`Fix Procfile for Railway deployment`
   - 点击 "Commit changes"

4. **等待Railway自动重新部署**
   - Railway会自动检测到GitHub的更新
   - 等待2-3分钟，查看部署状态

### 方法2：手动重新部署

如果Railway没有自动重新部署：
1. 在Railway项目页面
2. 点击 "Settings" 标签
3. 找到 "Redeploy" 或 "Deploy" 按钮
4. 点击重新部署

## 检查部署状态

部署完成后：
1. 查看Railway的 "Deployments" 标签
2. 确认最新部署显示 "Deploy successful"
3. 检查 "Metrics" 标签，确认服务正在运行
4. 在 "Settings" → "Domains" 中获取URL

## 如果还是离线

请把Railway的部署日志发给我，我会继续帮你排查问题！
