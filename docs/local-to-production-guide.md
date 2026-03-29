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
- `http://公网IP:8080/live/stream-001.m3u8`

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
- `http://你的域名/live/stream-001.m3u8`

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
- `https://你的域名/live/stream-001.m3u8`
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

## 8.1 精确测试方法

这一节不是说明“应该测什么”，而是直接说明“如何操作”和“预期看到什么结果”。

### 8.1.1 local 阶段测试

#### 1. 检查容器是否启动成功

操作：

```bash
cd docker
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml ps
```

预期结果：

- 能看到 `live-gateway` 和 `live-srs`
- 两个容器状态应为 `Up`
- 不应持续出现 `Restarting`

#### 2. 检查 Gateway 健康接口

操作：

在浏览器访问：

```text
http://127.0.0.1:8080/health
```

预期结果：

- 页面能打开
- 返回 `200` 类响应
- 表示 Gateway 已经启动成功

#### 3. 检查 Admin 页面

操作：

在浏览器访问：

```text
http://127.0.0.1:8080/admin/
```

预期结果：

- 能打开后台页面
- 页面静态资源可以正常加载
- 页面不应出现明显的 404 或整页空白

#### 4. 检查 API 是否可访问

操作：

在浏览器或接口工具访问：

```text
http://127.0.0.1:8080/api/v1/admin/streams
```

预期结果：

- 接口能够返回响应
- 即使返回空列表，也应当是“系统正常响应”，而不是连接失败

#### 5. 使用 OBS 进行本地推流

操作：

在 OBS 中设置：

- 服务器：`rtmp://127.0.0.1:1935/live`
- 串流密钥：`stream-001`

点击“开始推流”。

预期结果：

- OBS 不应立即报连接失败
- `live-srs` 日志中应出现推流接入记录
- 说明 SRS 已经接收到 RTMP 推流

#### 6. 检查本地播放地址

操作：

在浏览器访问：

```text
http://127.0.0.1:8080/live/stream-001.m3u8
```

预期结果：

- 地址可以正常打开，不应返回 404
- 如果播放器或浏览器支持，能够继续请求分片或子清单
- `live-gateway` 日志中应能看到 `/live/...` 请求

#### 7. 检查 WebSocket

操作：

打开前端页面或管理端页面，让其触发 WebSocket 建连。

预期结果：

- `live-gateway` 中不应出现 WebSocket 路径 404
- 前端页面不应出现持续的连接失败提示
- 当前阶段对应的协议应为 `ws://`

### 8.1.2 staging 阶段测试

#### 1. 公网 IP + HTTP 测试

操作：

确保 `.env.staging` 中：

- `DOMAIN_ENABLED=false`
- `HTTPS_ENABLED=false`
- `GATEWAY_BIND_PORT=8080`

启动后，在浏览器访问：

```text
http://公网IP:8080/health
http://公网IP:8080/admin/
http://公网IP:8080/live/stream-001.m3u8
```

预期结果：

- `/health` 可以打开
- `/admin/` 可以打开
- `/live/...` 不应返回 404
- 说明公网 IP、端口暴露、Gateway 与 SRS 链路都已打通

#### 2. 域名 + HTTP 测试

操作：

确保 `.env.staging` 中：

- `DOMAIN_ENABLED=true`
- `HTTPS_ENABLED=false`
- `PUBLIC_BASE_URL=http://你的域名`

并保证 DNS 已经正确指向服务器。然后访问：

```text
http://你的域名/health
http://你的域名/admin/
http://你的域名/live/stream-001.m3u8
```

预期结果：

- 三个地址都能打开
- 表示域名解析和 HTTP 回源都正常
- 此时页面和播放链路仍应使用 HTTP / WS

#### 3. 域名 + HTTPS 测试

操作：

确保 `.env.staging` 中：

- `DOMAIN_ENABLED=true`
- `HTTPS_ENABLED=true`
- `PUBLIC_BASE_URL=https://你的域名`
- `GATEWAY_INTERNAL_PORT=443`
- `GATEWAY_BIND_PORT=443`

并且 `docker/certs/` 中已经存在证书文件。然后访问：

```text
https://你的域名/health
https://你的域名/admin/
https://你的域名/live/stream-001.m3u8
```

预期结果：

- 浏览器能建立 HTTPS 连接
- `/health` 正常返回
- `/admin/` 正常加载
- `/live/...` 能访问，不应出现证书错误或 404
- 如果页面使用 WebSocket，此时应切换为 `wss://`

### 8.1.3 prod 阶段测试

#### 1. 检查 HTTPS 正式入口

操作：

在浏览器访问：

```text
https://你的正式域名/health
https://你的正式域名/admin/
https://你的正式域名/live/stream-001.m3u8
```

预期结果：

- 三个入口都应通过 HTTPS 访问
- 不再依赖 `http://域名:8080`
- 浏览器不应提示证书异常

#### 2. 检查 Cloudflare 回源是否正常

操作：

访问正式域名，并查看页面与接口是否能稳定返回。

预期结果：

- 域名能正常打开
- 不应出现持续性的 52x 回源错误
- 说明 Cloudflare 到 Gateway 的 HTTPS 回源是正常的

#### 3. 检查 OBS 推流是否仍然正常

操作：

在 OBS 中设置：

- 服务器：`rtmp://公网IP:1935/live`
- 串流密钥：`stream-001`

点击“开始推流”，然后访问：

```text
https://你的正式域名/live/stream-001.m3u8
```

预期结果：

- OBS 能正常连接并开始推流
- 播放地址能够访问
- 说明“OBS 走公网 IP，用户播放走 HTTPS 域名”这一正式链路已经成立

#### 4. 检查重复部署能力

操作：

重新执行：

```bash
cd docker
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

预期结果：

- 服务能再次被正常拉起
- 不需要修改业务代码
- 说明当前部署方式具备可重复上线能力

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
