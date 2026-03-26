# 快速部署指南

> 5 分钟上线你的直播辩论系统

---

## 第一步: 本地测试 (Windows)

```powershell
# 在 PowerShell 中运行
cd D:\Source\Python\task\demo2\Project
.\scripts\test-local.ps1
```

检查服务是否正常运行：
- API: http://localhost:8080/health
- HLS: https://localhost:8443/hls/

---

## 第二步: 上传到服务器

### 方法 A: 使用 SCP (推荐)

```powershell
# 在 PowerShell 中
cd D:\Source\Python\task\demo2\Project

# 压缩必要文件
# 然后上传
scp -r gateway root@106.14.254.19:/opt/debate-project/
scp Dockerfile Dockerfile.hls docker-compose.yml root@106.14.254.19:/opt/debate-project/
scp -r scripts cloudflared root@106.14.254.19:/opt/debate-project/
```

### 方法 B: 直接在服务器上操作

```bash
ssh root@106.14.254.19

# 创建目录
mkdir -p /opt/debate-project
cd /opt/debate-project

# 使用 git 克隆或手动上传文件
```

---

## 第三步: 服务器部署

```bash
ssh root@106.14.254.19

# 进入项目目录
cd /opt/debate-project

# 运行一键部署脚本
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

---

## 第四步: 启动 Cloudflare Tunnel

```bash
# 快速启动 (推荐用于测试)
cloudflared tunnel --url http://localhost:8080
```

你会看到类似这样的输出：

```
Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):
https://abc123-xyz456.trycloudflare.com
```

**复制这个 URL！** 这就是你的公网 HTTPS 地址。

---

## 第五步: 配置小程序

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)

2. 开发 → 开发管理 → 服务器域名

3. 添加以下域名：

```
# request 合法域名
https://abc123-xyz456.trycloudflare.com

# socket 合法域名
wss://abc123-xyz456.trycloudflare.com
```

4. 修改前端配置 `config/server-mode.node.js`:

```javascript
const REAL_SERVER_URL = 'https://abc123-xyz456.trycloudflare.com';
```

---

## 完成！测试访问

```bash
# 测试 API
curl https://abc123-xyz456.trycloudflare.com/health

# 测试 WebSocket
# 使用小程序或 WebSocket 测试工具
```

---

## 常用命令

```bash
# === 查看服务状态 ===
docker-compose ps

# === 查看日志 ===
docker-compose logs -f api
docker-compose logs -f hls

# === 重启服务 ===
docker-compose restart

# === 停止服务 ===
docker-compose down
```

---

## 故障排除

### Docker 服务启动失败

```bash
# 查看详细日志
docker-compose logs api

# 检查端口占用
netstat -tulpn | grep 8080
netstat -tulpn | grep 8443
```

### Cloudflare Tunnel 连接失败

```bash
# 确认服务在运行
curl http://localhost:8080/health

# 尝试重新启动 tunnel
cloudflared tunnel --url http://localhost:8080
```

### trycloudflare.com 域名每天变化

这是免费临时域名的正常行为。生产环境请：
1. 购买自己的域名
2. 在 Cloudflare 创建永久隧道
3. 配置 CNAME 记录

---

## 需要帮助？

查看完整文档: [DEPLOYMENT.md](./DEPLOYMENT.md)
