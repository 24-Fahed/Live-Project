# 从本地调试到服务器上线的操作教程

> 本文档面向当前项目的下一个版本，目标是指导你完成：
> 本地开发 -> 服务器联调 -> 正式上线。
> 核心原则：不同阶段的 IP、域名、端口切换通过 Docker 配置完成，而不是改代码。

## 1. 先理解三个阶段

下一个版本建议把整个部署过程分成三个阶段：

### 1.1 本地开发阶段

特点：

- 在自己电脑上运行 Docker
- 使用本机 IP 或局域网 IP
- 不依赖 DNS
- 主要验证功能是否跑通

这一阶段要回答的问题是：

- SRS 能不能收到 OBS 推流？
- Gateway 能不能正常工作？
- 播放地址能不能访问？
- 业务系统能不能感知媒体状态？

### 1.2 服务器联调阶段

特点：

- 部署到公网服务器
- 先使用公网 IP 调试
- 域名可以先不启用，或者最后再启用
- 重点是验证公网网络链路

这一阶段要回答的问题是：

- 公网 IP 能不能成功推流？
- 公网 IP 能不能成功播放？
- 服务器防火墙和 Docker 映射是否正确？
- 服务重启后能不能恢复？

### 1.3 正式上线阶段

特点：

- 启用域名
- 启用 Cloudflare DNS
- 使用正式访问地址
- 验证稳定性和可重复部署能力

这一阶段要回答的问题是：

- 域名访问是否正常？
- API / Admin / 播放是否都正常？
- 推流、播放、回调是否完整闭环？

## 2. 推荐的 Docker 组织方式

建议采用“基础 Compose + 环境覆盖文件 + 环境变量文件”的方式。

### 2.1 文件组织建议

```text
docker/
├─ docker-compose.yml
├─ docker-compose.local.yml
├─ docker-compose.staging.yml
├─ docker-compose.prod.yml
├─ .env.local
├─ .env.staging
├─ .env.prod
├─ start.sh
├─ start-staging.sh
└─ start-prod.sh
```

说明：

- `docker-compose.yml`：基础通用配置，包含 `gateway + srs`
- `docker-compose.local.yml`：本地开发时附加的环境文件声明
- `docker-compose.staging.yml`：服务器联调时附加的环境文件声明
- `docker-compose.prod.yml`：正式上线时附加的环境文件声明
- `.env.*`：每个阶段自己的地址、端口、域名配置

## 3. 当前 `.env` 字段的完整说明

这部分是为了和当前项目里的 `docker/.env.local`、`docker/.env.staging`、`docker/.env.prod` 保持完全一致。

### 3.1 运行阶段字段

| 字段 | 作用 | 是否必须配置 | 说明 |
| --- | --- | --- | --- |
| `APP_ENV` | 当前环境名 | 是 | 可取 `local` / `staging` / `production` |
| `APP_RUNTIME_MODE` | 当前运行模式 | 是 | 当前和 `APP_ENV` 保持一致即可 |
| `USE_DOMAIN` | 是否使用域名作为用户访问入口 | 是 | 本地一般为 `false`，正式上线一般为 `true` |
| `USE_PUBLIC_IP` | 是否使用公网 IP 参与访问策略 | 是 | 本地一般为 `false`，服务器联调和线上一般为 `true` |

### 3.2 网关访问地址字段

| 字段 | 作用 | 是否必须配置 | 说明 |
| --- | --- | --- | --- |
| `LOCAL_BASE_URL` | 本地开发阶段的网关基础地址 | 是 | 例如 `http://127.0.0.1:8080` |
| `STAGING_BASE_URL` | 服务器联调阶段的网关基础地址 | 建议配置 | 即使本地阶段不用，也建议保留 |
| `PUBLIC_BASE_URL` | 正式对外使用的基础地址 | 是 | 生产阶段通常是域名地址 |
| `PUBLIC_DOMAIN` | 正式域名 | 生产阶段必须 | 本地和联调阶段可以留空，属于预留字段 |
| `GATEWAY_PORT` | 网关对外端口 | 是 | 当前默认 `8080` |
| `USE_CLOUDFLARE_DNS` | 是否进入 Cloudflare DNS 场景 | 生产阶段建议配置 | 本地和联调阶段通常为 `false`，属于预留控制字段 |

### 3.3 媒体服务器字段

| 字段 | 作用 | 是否必须配置 | 说明 |
| --- | --- | --- | --- |
| `SRS_HOST` | Gateway 访问 SRS 的主机名 | 是 | 当前 Docker 内固定使用 `srs` |
| `SRS_RTMP_PORT` | SRS RTMP 推流端口 | 是 | 当前默认 `1935` |
| `SRS_HTTP_PORT` | SRS HTTP 播放端口 | 是 | 当前默认 `8088` |
| `SRS_APP` | SRS 中的应用名 | 是 | 当前默认 `live` |
| `SRS_PLAY_PATH_PREFIX` | 网关侧统一播放路径前缀 | 是 | 当前默认 `/live` |
| `ALLOW_DIRECT_IP_PUSH` | 是否允许 OBS 直接用公网 IP 推流 | 是 | 当前建议保持 `true` |

### 3.4 推流地址字段

| 字段 | 作用 | 是否必须配置 | 说明 |
| --- | --- | --- | --- |
| `LOCAL_PUSH_BASE` | 本地开发阶段 OBS 推流基础地址 | 是 | 例如 `rtmp://127.0.0.1:1935/live` |
| `STAGING_PUSH_BASE` | 服务器联调阶段 OBS 推流基础地址 | 建议配置 | 联调阶段通常改为公网 IP |
| `PRODUCTION_PUSH_BASE` | 正式上线阶段 OBS 推流基础地址 | 建议配置 | 当前阶段通常仍然是公网 IP |

说明：

- 这些字段不是让前端使用的，而是给网关的 `media` 子系统生成推流地址使用。
- 即使当前阶段暂时用不到，也建议保留，属于“环境模板字段”，不是无效字段。

### 3.5 安全字段

| 字段 | 作用 | 是否必须配置 | 说明 |
| --- | --- | --- | --- |
| `SRS_CALLBACK_TOKEN` | SRS 回调到 Gateway 时的校验令牌 | 当前建议保留 | 这是安全预留字段，未来接 SRS 回调时会真正用到 |
| `MEDIA_ADMIN_TOKEN` | 媒体管理相关的额外安全令牌 | 当前建议保留 | 也是安全预留字段，当前版本可以先不启用复杂逻辑 |

### 3.6 哪些字段当前属于“预留，不一定要改”

下面这些字段当前建议保留在 `.env.*` 中，但在某些阶段可以先不改，或者先保留默认值：

| 字段 | 当前是否可以暂时不改 | 原因 |
| --- | --- | --- |
| `PUBLIC_DOMAIN` | 可以 | 本地和联调阶段通常不用域名 |
| `USE_CLOUDFLARE_DNS` | 可以 | 本地和联调阶段通常不启用 |
| `STAGING_BASE_URL` | 本地阶段可以 | 但建议先保留，避免后期漏配 |
| `PRODUCTION_PUSH_BASE` | 本地和联调阶段可以 | 正式上线前再确认即可 |
| `SRS_CALLBACK_TOKEN` | 可以先保留默认值 | 当前代码已预留回调校验入口，但你还没正式接完整回调流 |
| `MEDIA_ADMIN_TOKEN` | 可以先保留默认值 | 当前属于安全预留项 |

结论是：

- “预留字段”不等于“无用字段”
- 它们的意义是让三套环境模板结构保持一致，后续切换环境时不需要补字段

## 4. 三套 `.env` 文件配置示例

### 4.1 `.env.local` 配置示例

适用于本地 Docker 调试。

当前项目中的实际内容是：

```env
APP_ENV=local
APP_RUNTIME_MODE=local
USE_DOMAIN=false
USE_PUBLIC_IP=false
LOCAL_BASE_URL=http://127.0.0.1:8080
STAGING_BASE_URL=http://127.0.0.1:8080
PUBLIC_BASE_URL=http://127.0.0.1:8080
PUBLIC_DOMAIN=
USE_CLOUDFLARE_DNS=false
GATEWAY_PORT=8080
SRS_HOST=srs
SRS_RTMP_PORT=1935
SRS_HTTP_PORT=8088
SRS_APP=live
SRS_PLAY_PATH_PREFIX=/live
ALLOW_DIRECT_IP_PUSH=true
LOCAL_PUSH_BASE=rtmp://127.0.0.1:1935/live
STAGING_PUSH_BASE=rtmp://127.0.0.1:1935/live
PRODUCTION_PUSH_BASE=rtmp://127.0.0.1:1935/live
SRS_CALLBACK_TOKEN=replace-me
MEDIA_ADMIN_TOKEN=replace-me
```

说明：

- 这里的 `SRS_HOST=srs` 是对的，因为 Gateway 在 Docker 网络里访问 SRS，用服务名访问。
- 这里的 `127.0.0.1` 是“你在宿主机访问网关/推流时使用的地址”。
- `STAGING_BASE_URL` 和 `PRODUCTION_PUSH_BASE` 虽然本地暂时用不到，但建议保留，属于模板统一字段。

### 4.2 `.env.staging` 配置示例

适用于服务器联调阶段。

当前项目中的实际内容是：

```env
APP_ENV=staging
APP_RUNTIME_MODE=staging
USE_DOMAIN=false
USE_PUBLIC_IP=true
LOCAL_BASE_URL=http://127.0.0.1:8080
STAGING_BASE_URL=http://YOUR_PUBLIC_IP:8080
PUBLIC_BASE_URL=http://YOUR_PUBLIC_IP:8080
PUBLIC_DOMAIN=
USE_CLOUDFLARE_DNS=false
GATEWAY_PORT=8080
SRS_HOST=srs
SRS_RTMP_PORT=1935
SRS_HTTP_PORT=8088
SRS_APP=live
SRS_PLAY_PATH_PREFIX=/live
ALLOW_DIRECT_IP_PUSH=true
LOCAL_PUSH_BASE=rtmp://127.0.0.1:1935/live
STAGING_PUSH_BASE=rtmp://YOUR_PUBLIC_IP:1935/live
PRODUCTION_PUSH_BASE=rtmp://YOUR_PUBLIC_IP:1935/live
SRS_CALLBACK_TOKEN=replace-me
MEDIA_ADMIN_TOKEN=replace-me
```

你真正需要改的字段主要是：

- `STAGING_BASE_URL`
- `PUBLIC_BASE_URL`
- `STAGING_PUSH_BASE`
- `PRODUCTION_PUSH_BASE`

把其中的 `YOUR_PUBLIC_IP` 替换成你的公网 IP 即可。

### 4.3 `.env.prod` 配置示例

适用于正式上线阶段。

当前项目中的实际内容是：

```env
APP_ENV=production
APP_RUNTIME_MODE=production
USE_DOMAIN=true
USE_PUBLIC_IP=true
LOCAL_BASE_URL=http://127.0.0.1:8080
STAGING_BASE_URL=http://YOUR_PUBLIC_IP:8080
PUBLIC_BASE_URL=http://test.com:8080
PUBLIC_DOMAIN=test.com
USE_CLOUDFLARE_DNS=true
GATEWAY_PORT=8080
SRS_HOST=srs
SRS_RTMP_PORT=1935
SRS_HTTP_PORT=8088
SRS_APP=live
SRS_PLAY_PATH_PREFIX=/live
ALLOW_DIRECT_IP_PUSH=true
LOCAL_PUSH_BASE=rtmp://127.0.0.1:1935/live
STAGING_PUSH_BASE=rtmp://YOUR_PUBLIC_IP:1935/live
PRODUCTION_PUSH_BASE=rtmp://YOUR_PUBLIC_IP:1935/live
SRS_CALLBACK_TOKEN=replace-me
MEDIA_ADMIN_TOKEN=replace-me
```

你真正需要改的字段主要是：

- `STAGING_BASE_URL`
- `PUBLIC_BASE_URL`
- `PUBLIC_DOMAIN`
- `STAGING_PUSH_BASE`
- `PRODUCTION_PUSH_BASE`

说明：

- 当前方案下，正式上线时用户访问一般走域名。
- 但 OBS 仍然可以继续通过公网 IP 推流，所以 `PRODUCTION_PUSH_BASE` 依然可以写公网 IP。

## 5. 推荐的 Compose 启动方式

### 5.1 本地开发启动

```bash
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

### 5.2 服务器联调启动

```bash
docker compose --env-file .env.staging -f docker-compose.yml -f docker-compose.staging.yml up -d --build
```

### 5.3 正式上线启动

```bash
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## 6. 本地开发阶段怎么做

### 6.1 第一步：准备本地 Docker 环境

确保本地已经安装：

- Docker
- Docker Compose
- OBS

### 6.2 第二步：启动本地服务

运行：

```bash
cd docker
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

### 6.3 第三步：检查服务状态

要确认以下内容：

- Gateway 是否启动成功
- SRS 是否启动成功
- 管理后台是否可访问
- 媒体播放代理是否可访问

建议检查：

- `http://127.0.0.1:8080/health`
- `http://127.0.0.1:8080/admin/`

### 6.4 第四步：OBS 本地推流测试

在 OBS 中配置推流地址：

```text
rtmp://127.0.0.1:1935/live
```

推流码可以先用简单流名，例如：

```text
stream-001
```

### 6.5 第五步：本地播放测试

通过网关统一暴露的播放地址测试，例如：

```text
http://127.0.0.1:8080/live/stream-001.m3u8
```

### 6.6 本地阶段完成标准

当以下条件全部满足时，可以认为本地调试完成：

- OBS 能稳定推流到本地 SRS
- Gateway 正常工作
- 播放地址可访问
- 管理端能看到对应直播状态
- 容器重启后配置不需要改代码

## 7. 服务器联调阶段怎么做

### 7.1 第一步：准备服务器

服务器需要完成：

- 安装 Docker
- 安装 Docker Compose
- 开放端口：
  - `8080`
  - `1935`
  - 如有需要也开放 `8088`

### 7.2 第二步：修改 `.env.staging`

把这些字段替换成你的真实公网 IP：

- `STAGING_BASE_URL`
- `PUBLIC_BASE_URL`
- `STAGING_PUSH_BASE`
- `PRODUCTION_PUSH_BASE`

### 7.3 第三步：上传并部署

推荐流程是：

1. 本地构建并确认版本可用
2. 上传项目代码到服务器，或者通过 git pull 获取
3. 在服务器执行：

```bash
cd docker
docker compose --env-file .env.staging -f docker-compose.yml -f docker-compose.staging.yml up -d --build
```

### 7.4 第四步：公网 IP 推流测试

在 OBS 中配置：

```text
rtmp://公网IP:1935/live
```

流名仍然可以使用：

```text
stream-001
```

### 7.5 第五步：公网 IP 播放测试

测试：

```text
http://公网IP:8080/live/stream-001.m3u8
```

### 7.6 第六步：检查联动能力

你要重点检查：

- 推流成功后，管理端是否能感知
- 播放是否连续稳定
- 网关是否能正确返回播放地址
- 回调是否正常
- Docker 重启后服务是否恢复

### 7.7 服务器联调完成标准

当以下条件满足时，可以进入正式上线：

- 公网 IP 推流成功
- 公网 IP 播放成功
- 管理端联动正常
- Docker 可重复部署
- 环境切换不需要改代码

## 8. 正式上线阶段怎么做

### 8.1 第一步：配置域名

在 Cloudflare 中配置：

- 域名 A 记录指向公网 IP

例如：

- `test.com -> 公网IP`

### 8.2 第二步：修改 `.env.prod`

把这些字段替换成你的真实域名和公网 IP：

- `STAGING_BASE_URL`
- `PUBLIC_BASE_URL`
- `PUBLIC_DOMAIN`
- `STAGING_PUSH_BASE`
- `PRODUCTION_PUSH_BASE`

### 8.3 第三步：启动正式环境

在服务器执行：

```bash
cd docker
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 8.4 第四步：验证域名访问

需要测试：

- `http://test.com:8080/health`
- `http://test.com:8080/admin/`
- `http://test.com:8080/live/stream-001.m3u8`

### 8.5 第五步：保留最简单推流方式

为了减少风险，正式上线阶段 OBS 仍然可以继续使用：

```text
rtmp://公网IP:1935/live
```

也就是说：

- 用户访问走域名
- 主播推流先走公网 IP

这样更容易先把系统稳定下来。

### 8.6 正式上线完成标准

当以下条件满足时，可以认为系统已经“上线”：

- 域名访问稳定
- Admin 正常
- 播放正常
- OBS 推流正常
- 回调与状态同步正常
- Docker 部署可重复执行
- 换环境不需要改代码

## 9. 你每个阶段到底在调试什么

### 9.1 本地开发阶段调试的是“功能闭环”

你在本地不是在调公网，而是在调：

- 代码逻辑是否成立
- 推流到播放是否闭环
- 媒体层和业务层是否打通

### 9.2 服务器联调阶段调试的是“网络闭环”

你在服务器阶段不是在做最终上线展示，而是在调：

- 公网端口是否通
- Docker 部署是否可靠
- 公网推流和播放是否真实可用

### 9.3 正式上线阶段调试的是“稳定运行能力”

你在正式上线阶段要确认的是：

- 域名是否可用
- 服务是否稳定
- 部署是否标准化
- 是否可以不用改代码完成环境切换

## 10. 最后给你的执行建议

如果你想把复杂度控制在你目前可接受的范围内，我建议你严格按下面顺序推进：

1. 先把本地 Docker 跑通
2. 先确认 OBS -> SRS -> Gateway -> 播放地址 这个闭环成立
3. 再把同一套 Docker 方案搬到公网服务器
4. 先用公网 IP 联调
5. 最后再切域名

不要一开始就同时处理：

- 域名
- DNS
- SRS
- Gateway
- 回调
- 上线稳定性

这样你会很容易把问题混在一起。

最好的方式是：

- 本地调功能
- 服务器调网络
- 上线调稳定性

这三个阶段分开，你的推进会轻松很多。

