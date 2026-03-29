# 从本地调试到服务器上线的操作教程

> 本文档对应 `v0.1.2` 方案。
> 目标是让我们通过同一套代码，在不同 Docker 环境变量下完成：
> `local -> staging -> prod`。

## 1. 三个阶段的职责

### 1.1 local

`local` 只负责业务闭环和基础联调。

重点验证：

- Gateway 是否正常启动
- SRS 是否正常启动
- OBS 是否能推流到本地 SRS
- `/live/...` 是否能播放
- Admin、API、WebSocket 是否工作正常

在这一阶段：

- 不要求域名
- 不要求 HTTPS
- 不要求 Cloudflare

### 1.2 staging

`staging` 是公网集成测试环境。

它不是正式上线环境，而是用来按能力增量逐步验证：

1. 公网 IP + HTTP
2. 域名 + HTTP
3. 域名 + HTTPS

这一阶段的重点不是新业务功能，而是：

- 公网 IP 连通性
- 域名解析是否正常
- Cloudflare DNS 是否正确
- HTTPS / WSS 是否正确
- 回源到 Gateway 是否正确

### 1.3 prod

`prod` 是正式上线环境。

当前版本目标是：

- `Admin` 走 HTTPS
- `API` 走 HTTPS
- `/live` 播放走 HTTPS
- WebSocket 走 WSS
- OBS 继续通过公网 IP 的 RTMP 端口推流

## 2. 当前版本的协议策略

### 2.1 用户访问入口

- local：`http://127.0.0.1:8080`
- staging 第一阶段：`http://公网IP:8080`
- staging 第二阶段：`http://域名`
- staging 第三阶段 / prod：`https://域名`

### 2.2 WebSocket

- HTTP 页面对应：`ws://host/ws`
- HTTPS 页面对应：`wss://host/ws`

### 2.3 OBS 推流

无论 staging 还是 prod，当前都保持最简单方案：

- `rtmp://公网IP:1935/live`

说明：

- Cloudflare 负责 HTTP/HTTPS 入口
- RTMP 不走 Cloudflare 代理
- 因此正式上线后，OBS 依然建议继续推送到公网 IP

## 3. Docker 文件组织

```text
docker/
├─ docker-compose.yml
├─ docker-compose.local.yml
├─ docker-compose.staging.yml
├─ docker-compose.prod.yml
├─ .env
├─ .env.local
├─ .env.staging
├─ .env.prod
├─ certs/
│  └─ README.md
└─ srs/
```

说明：

- `docker-compose.yml`：基础服务定义
- `docker-compose.local.yml`：local 环境变量入口
- `docker-compose.staging.yml`：staging 环境变量入口
- `docker-compose.prod.yml`：prod 环境变量入口
- `certs/`：存放 Cloudflare Origin CA 证书和私钥

## 4. `.env` 设计原则

当前阶段继续保留：

- `.env.local`
- `.env.staging`
- `.env.prod`

不再继续拆成更多物理文件，但在每个文件内部统一分组：

1. Runtime
2. Mirror / Build Source
3. Access Strategy
4. Gateway Ports
5. HTTPS / TLS
6. Media
7. WeChat
8. Security

这样做的目标是：

- 结构统一
- 便于比较环境差异
- 不需要通过改代码切换协议与入口

## 5. 三套 `.env` 里的关键开关

### 5.1 Access Strategy

| 字段 | 作用 |
| --- | --- |
| `USE_DOMAIN` | 是否让用户入口使用域名 |
| `DOMAIN_ENABLED` | 是否启用域名模式 |
| `USE_PUBLIC_IP` | 是否启用公网 IP 相关逻辑 |
| `CLOUDFLARE_ENABLED` | 是否进入 Cloudflare 回源场景 |
| `USE_CLOUDFLARE_DNS` | 是否使用 Cloudflare DNS 场景 |

### 5.2 HTTPS / TLS

| 字段 | 作用 |
| --- | --- |
| `HTTPS_ENABLED` | 是否启用 HTTPS 模式 |
| `TLS_PROVIDER` | 当前证书来源说明 |
| `TLS_CERT_FILE` | 容器内证书路径 |
| `TLS_KEY_FILE` | 容器内私钥路径 |

### 5.3 Gateway Ports

| 字段 | 作用 |
| --- | --- |
| `GATEWAY_HOST` | 容器内监听地址 |
| `GATEWAY_PORT` | 兼容字段，给旧逻辑保底 |
| `GATEWAY_INTERNAL_PORT` | 容器内实际监听端口 |
| `GATEWAY_BIND_PORT` | 宿主机对外暴露端口 |
| `HTTP_PORT` | HTTP 标准端口说明 |
| `HTTPS_PORT` | HTTPS 标准端口说明 |

## 6. 如何理解 staging 的三步测试

### 6.1 第一步：公网 IP + HTTP

推荐配置：

- `USE_DOMAIN=false`
- `DOMAIN_ENABLED=false`
- `HTTPS_ENABLED=false`
- `CLOUDFLARE_ENABLED=false`
- `GATEWAY_INTERNAL_PORT=8080`
- `GATEWAY_BIND_PORT=8080`

访问入口：

- `http://公网IP:8080/admin/`
- `http://公网IP:8080/api/...`
- `http://公网IP:8080/live/live/stream-001.m3u8`

### 6.2 第二步：域名 + HTTP

推荐配置：

- `USE_DOMAIN=true`
- `DOMAIN_ENABLED=true`
- `HTTPS_ENABLED=false`
- `CLOUDFLARE_ENABLED=false`
- `PUBLIC_DOMAIN=你的域名`
- `PUBLIC_BASE_URL=http://你的域名`
- `GATEWAY_INTERNAL_PORT=8080`
- `GATEWAY_BIND_PORT=8080`

访问入口：

- `http://你的域名/admin/`
- `http://你的域名/api/...`
- `http://你的域名/live/live/stream-001.m3u8`

### 6.3 第三步：域名 + HTTPS

推荐配置：

- `USE_DOMAIN=true`
- `DOMAIN_ENABLED=true`
- `HTTPS_ENABLED=true`
- `CLOUDFLARE_ENABLED=true`
- `USE_CLOUDFLARE_DNS=true`
- `PUBLIC_DOMAIN=你的域名`
- `PUBLIC_BASE_URL=https://你的域名`
- `GATEWAY_INTERNAL_PORT=443`
- `GATEWAY_BIND_PORT=443`

同时需要：

- 将 Cloudflare SSL/TLS 设为 `Full (strict)`
- 将证书与私钥放入 `docker/certs/origin.crt` 和 `docker/certs/origin.key`

访问入口：

- `https://你的域名/admin/`
- `https://你的域名/api/...`
- `https://你的域名/live/live/stream-001.m3u8`
- `wss://你的域名/ws`

## 7. Compose 启动命令

### 7.1 local

```bash
cd docker
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

### 7.2 staging

```bash
cd docker
docker compose --env-file .env.staging -f docker-compose.yml -f docker-compose.staging.yml up -d --build
```

### 7.3 prod

```bash
cd docker
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## 8. 证书准备

当 `HTTPS_ENABLED=true` 时，Gateway 会直接以 HTTPS 模式启动。

因此必须保证容器内存在：

- `/app/certs/origin.crt`
- `/app/certs/origin.key`

在当前 Docker 结构下，对应宿主机目录为：

- `docker/certs/origin.crt`
- `docker/certs/origin.key`

如果缺少证书文件，Gateway 会直接启动失败。

## 9. 每个阶段的完成标准

### 9.1 local 完成标准

- OBS 能推流到本地 SRS
- Admin 正常
- API 正常
- `/live/...` 正常
- WebSocket 正常

### 9.2 staging 完成标准

- 公网 IP 能访问 Gateway
- 域名解析正确
- Cloudflare 配置正确
- HTTPS / WSS 正常
- `/live` 在公网环境下稳定可访问

### 9.3 prod 完成标准

- `Admin / API / /live / WebSocket` 全部统一纳入 HTTPS / WSS
- Cloudflare `Full (strict)` 回源正常
- OBS 能稳定通过公网 IP 推流
- Docker 可重复部署
- 无需改代码即可切换环境
