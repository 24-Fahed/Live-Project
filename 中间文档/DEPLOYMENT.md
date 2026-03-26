# 直播辩论系统 Cloudflare Tunnel 部署方案

> 版本: v1.0
> 更新时间: 2025-03-26
> 服务器: Ubuntu @ 106.14.254.19

---

## 一、项目架构说明

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户访问层                                │
├─────────────────────────────────────────────────────────────────┤
│  小程序/浏览器  ←→  Cloudflare Tunnel (HTTPS)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Ubuntu 服务器                              │
│                       106.14.254.19                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │   Docker 容器    │  │   Docker 容器    │                      │
│  ├─────────────────┤  ├─────────────────┤                      │
│  │  FastAPI 主服务  │  │   HLS HTTPS     │                      │
│  │  端口: 8080      │  │   端口: 8443    │                      │
│  │  - API 路由      │  │  - HLS 流文件   │                      │
│  │  - WebSocket     │  │  - HTTPS (自签) │                      │
│  │  - 后台管理      │  │                 │                      │
│  └─────────────────┘  └─────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### 服务端口分配

| 服务 | 内部端口 | 外部访问协议 | 用途 |
|------|----------|-------------|------|
| FastAPI 主服务 | 8080 | HTTP (via Cloudflare) | API、WebSocket、后台管理 |
| HLS 流服务 | 8443 | HTTPS (via Cloudflare) | 视频流文件托管 |

### Cloudflare Tunnel 路由规则

| 外部路径 | 内部目标 | 协议 |
|----------|----------|------|
| `https://xxx.trycloudflare.com/api/*` | `http://localhost:8080/api/*` | HTTP |
| `https://xxx.trycloudflare.com/ws` | `http://localhost:8080/ws` | WebSocket |
| `https://xxx.trycloudflare.com/admin/*` | `http://localhost:8080/admin/*` | HTTP |
| `https://xxx.trycloudflare.com/hls/*` | `https://localhost:8443/hls/*` | HTTPS |

---

## 二、本地 Docker 测试环境搭建

### 步骤 1: 创建 Docker 配置文件

在项目根目录 `D:\Source\Python\task\demo2\Project` 下创建以下文件：

#### 2.1 `Dockerfile` (FastAPI 主服务)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY gateway/app ./app
COPY gateway/static ./static

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### 2.2 `Dockerfile.hls` (HLS HTTPS 服务)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖和 OpenSSL
RUN apt-get update && apt-get install -y \
    gcc \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY gateway/app ./app
COPY gateway/static ./static

# 暴露端口
EXPOSE 8443

# 启动 HLS 服务
CMD ["python", "-c", "from app.subsystems.hls.server import HLSServer; s = HLSServer(); s.start()"]
```

#### 2.3 `docker-compose.yml`

```yaml
version: '3.8'

services:
  # FastAPI 主服务
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: debate-api
    ports:
      - "8080:8080"
    volumes:
      - ./gateway/static:/app/static
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    networks:
      - debate-net

  # HLS HTTPS 服务
  hls:
    build:
      context: .
      dockerfile: Dockerfile.hls
    container_name: debate-hls
    ports:
      - "8443:8443"
    volumes:
      - ./gateway/static:/app/static
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    networks:
      - debate-net

networks:
  debate-net:
    driver: bridge
```

#### 2.4 `.dockerignore`

```
node_modules
.git
.unpackage
dist
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.env
.venv
venv/
ENV/
```

### 步骤 2: 本地构建和测试

在项目根目录打开终端：

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 测试服务
curl http://localhost:8080/health
curl -k https://localhost:8443/hls/
```

### 步骤 3: 停止本地测试

```bash
docker-compose down
```

---

## 三、服务器部署

### 步骤 1: 准备服务器

SSH 连接到服务器：

```bash
ssh root@106.14.254.19
```

安装 Docker 和 Docker Compose：

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 启动 Docker 服务
systemctl start docker
systemctl enable docker

# 安装 Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 步骤 2: 上传项目文件

在本地 Windows 机器上，使用 SCP 上传项目：

```powershell
# 在 PowerShell 中执行
cd D:\Source\Python\task\demo2\Project

# 压缩必要文件（排除 node_modules 等）
# 然后上传到服务器
```

或者在服务器上直接克隆/拉取代码：

```bash
# 在服务器上
cd /opt
mkdir debate-project
cd debate-project

# 如果使用 Git
git clone <你的仓库地址> .

# 或者使用 SCP/SFTP 从本地上传
```

确保以下目录结构：

```
/opt/debate-project/
├── Dockerfile
├── Dockerfile.hls
├── docker-compose.yml
├── gateway/
│   ├── app/
│   ├── static/
│   └── requirements.txt
```

### 步骤 3: 启动服务

```bash
cd /opt/debate-project

# 构建并启动
docker-compose up -d

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f api
docker-compose logs -f hls
```

### 步骤 4: 配置防火墙

```bash
# 允许 SSH
ufw allow 22/tcp

# Cloudflare Tunnel 不需要开放额外端口到公网
# 因为 tunnel 会主动连接 Cloudflare

# 启用防火墙
ufw enable
```

---

## 四、Cloudflare Tunnel 配置

### 方案 A: 使用 cloudflared (推荐)

#### 步骤 1: 安装 cloudflared

```bash
# 在服务器上下载并安装
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb

# 验证安装
cloudflared --version
```

#### 步骤 2: 创建隧道配置

创建配置文件 `/etc/cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /root/.cloudflared/<TUNNEL_ID>.json

ingress:
  # HLS 流服务 (HTTPS → HTTPS)
  - hostname: <YOUR_SUBDOMAIN>.trycloudflare.com
    service: https://localhost:8443
    originRequest:
      noTLSVerify: true  # 忽略自签名证书错误

  # 或者使用路径规则
  - service: http://localhost:8080
    path: /api/*

  - service: http://localhost:8080
    path: /admin/*

  - service: http://localhost:8080
    path: /ws
    protocol: websocket

  # 默认规则
  - service: http_status:404
```

#### 步骤 3: 创建并启动隧道

```bash
# 登录 Cloudflare (会打开浏览器授权)
cloudflared tunnel login

# 创建隧道
cloudflared tunnel create debate-tunnel

# 记下返回的 TUNNEL_ID

# 配置隧道
cloudflared tunnel route dns <TUNNEL_ID> debate.your-domain.com

# 或者不配置 DNS，使用提供的 trycloudflare.com 子域名

# 启动隧道测试
cloudflared tunnel --config /etc/cloudflared/config.yml run <TUNNEL_ID>

# 安装为系统服务
cloudflared service install
systemctl enable cloudflared
systemctl start cloudflared
```

#### 步骤 4: 获取公网 URL

启动后会显示分配的临时 URL：

```
https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.trycloudflare.com
```

### 方案 B: 快速启动 (最简单)

```bash
# 直接启动，自动获取临时 URL
cloudflared tunnel --url http://localhost:8080

# 或者同时映射多个端口
# 终端 1:
cloudflared tunnel --url http://localhost:8080

# 终端 2:
cloudflared tunnel --url https://localhost:8443 --no-tls-verify
```

### 方案 C: Docker 部署 cloudflared

修改 `docker-compose.yml` 添加：

```yaml
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: cloudflared
    command: tunnel run
    environment:
      - TUNNEL_TOKEN=<你的隧道令牌>
    restart: unless-stopped
    networks:
      - debate-net
```

获取隧道令牌：

1. 访问 Cloudflare Zero Dashboard
2. 创建新的隧道
3. 复制令牌

---

## 五、小程序域名配置

### 获取 Cloudflare Tunnel 域名

启动 tunnel 后，你会得到类似这样的 URL：

```
https://abc123def456.trycloudflare.com
```

### 微信小程序配置

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入你的小程序 → 开发 → 开发管理 → 服务器域名
3. 配置以下域名：

```
# request 合法域名
https://abc123def456.trycloudflare.com

# socket 合法域名
wss://abc123def456.trycloudflare.com/ws

# uploadFile 合法域名
https://abc123def456.trycloudflare.com

# downloadFile 合法域名
https://abc123def456.trycloudflare.com
```

**注意**: trycloudflare.com 域名每天都会变化，不适合生产环境。

### 推荐方案：使用自己的域名

1. 购买域名 (如从阿里云、腾讯云)
2. 将域名添加到 Cloudflare
3. 创建永久隧道，配置 CNAME

---

## 六、验证部署

### 测试 API

```bash
# 健康检查
curl https://<your-tunnel-url>.trycloudflare.com/health

# API 测试
curl https://<your-tunnel-url>.trycloudflare.com/api/v1/streams
```

### 测试 WebSocket

使用 WebSocket 测试工具连接：

```
wss://<your-tunnel-url>.trycloudflare.com/ws
```

### 测试 HLS 流

```
https://<your-tunnel-url>.trycloudflare.com/hls/<stream-name>/index.m3u8
```

---

## 七、常见问题

### Q1: trycloudflare.com 域名每天变

**解决方案**: 使用自己的域名，配置 Cloudflare 永久隧道。

### Q2: HLS 自签名证书报错

**解决方案**:
- 在 cloudflared 配置中添加 `noTLSVerify: true`
- 或者为 HLS 服务申请 Let's Encrypt 证书

### Q3: WebSocket 连接失败

**检查**:
1. Cloudflare Tunnel 配置中是否正确设置了 `protocol: websocket`
2. 小程序是否已配置 wss 合法域名

### Q4: 服务器重启后服务未启动

**解决方案**:
```bash
# 确保 Docker 服务开机自启
systemctl enable docker

# 确保 docker-compose 服务开机自启
# 在 /etc/systemd/system/debate.service 创建服务文件
```

---

## 八、生产环境建议

1. **域名**: 购买自己的域名，不使用 trycloudflare.com
2. **证书**: 使用 Let's Encrypt 替代自签名证书
3. **监控**: 配置日志收集和监控告警
4. **备份**: 定期备份数据文件
5. **安全**: 配置防火墙、 fail2ban

---

## 九、快速命令参考

```bash
# === 本地 ===
# 构建和测试
docker-compose build && docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# === 服务器 ===
# 启动服务
cd /opt/debate-project && docker-compose up -d

# 查看状态
docker-compose ps

# 重启服务
docker-compose restart

# Cloudflare Tunnel
cloudflared tunnel run <TUNNEL_ID>

# 查看隧道状态
systemctl status cloudflared
```
