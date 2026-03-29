# Gateway 配置说明

本文档专门解释：`gateway/app/infra/*/config.py` 里的配置是怎么被读取和生效的。

这份文档的目标不是讲业务，而是回答配置阅读者最容易困惑的问题，例如：

- `APP_ENV` 是什么？
- `APP_RUNTIME_MODE` 为什么也存在？
- `current_base_url` 为什么要先看 `APP_RUNTIME_MODE`？
- `local`、`staging`、`production` 分别代表什么？

## 1. 配置文件分层

当前网关里的 `config.py` 大致分成几类：

### 1.1 `infra/runtime/config.py`

负责“当前网关运行在哪个阶段”。

它决定：

- 当前是 `local`、`staging` 还是 `production`
- 网关应该返回哪一个基础地址
- 业务模块在生成外部访问 URL 时，应该使用本地地址、联调地址还是公开地址

### 1.2 `infra/edge/config.py`

负责“系统如何被外部访问”。

它描述的是：

- 域名
- 网关端口
- 是否启用 Cloudflare DNS
- 是否启用 HTTPS / TLS

这类配置属于接入层，不属于业务层。

### 1.3 `infra/media_config/config.py`

负责“网关如何和 SRS 这种媒体服务协作”。

它描述的是：

- SRS 的主机名和端口
- RTMP 推流基础地址
- HLS 播放前缀
- 媒体回调 token

### 1.4 `infra/auth/config.py`

负责鉴权与身份相关配置：

- JWT 签名参数
- 白名单路径
- 微信登录凭据

### 1.5 `infra/static/config.py`

负责静态资源挂载规则，例如：

- `/admin`
- `/static`

## 2. `APP_ENV` 和 `APP_RUNTIME_MODE` 的区别

这两个字段看起来很像，所以最容易让人困惑。

### 2.1 `APP_ENV`

`APP_ENV` 是“环境标签”。

常见取值：

- `local`
- `staging`
- `production`

它更像是在说：

“我现在处在什么部署环境里。”

### 2.2 `APP_RUNTIME_MODE`

`APP_RUNTIME_MODE` 是“运行时行为开关”。

它更像是在说：

“网关现在应该按哪一种行为返回地址和切换逻辑。”

在当前项目里，它通常和 `APP_ENV` 一致，但单独保留它有两个好处：

1. 配置语义更清楚  
   `APP_ENV` 只是一个环境标签，`APP_RUNTIME_MODE` 明确表示“这会直接影响运行时逻辑”。

2. 后续扩展更灵活  
   如果未来出现“同样是 staging 环境，但运行策略不完全一样”的场景，就不需要强行复用一个字段表达所有含义。

## 3. 为什么 `current_base_url` 要这样写

当前代码里最容易让读者疑惑的是这段逻辑：

```python
mode = (self.APP_RUNTIME_MODE or self.APP_ENV or "local").lower()
```

它的真实含义是：

1. 优先使用 `APP_RUNTIME_MODE`
2. 如果没有设置，再退回 `APP_ENV`
3. 如果两者都没有，就默认把系统当成 `local`

为什么最后要默认成 `local`？

因为对于这个项目来说，最安全的默认行为就是：

- 使用本地开发地址
- 不假设自己已经处于 staging 或 production

这样即使开发者忘记配置环境变量，系统也会退回到最保守、最容易理解的本地行为。

## 4. `current_base_url` 实际在做什么

它的职责不是给浏览器发请求，而是：

**给网关内部其他模块提供“当前应该对外暴露哪个基础地址”的统一答案。**

例如媒体模块生成播放地址时，并不直接自己判断当前是不是生产环境，而是调用：

- `runtime_settings.current_base_url`

这样做的好处是：

- 业务模块不需要重复写环境判断
- 地址切换逻辑集中在基础设施层
- 后续改动不容易牵扯多个子系统

## 5. `local`、`staging`、`production` 在这个项目里分别是什么

### 5.1 `local`

表示本地开发与本地 Docker 调试阶段。

典型特征：

- 不依赖域名
- 不依赖 Cloudflare
- 默认使用本机地址，如 `http://127.0.0.1:8080`

### 5.2 `staging`

表示公网集成测试阶段。

典型特征：

- 已部署到公网服务器
- 但还不等于正式上线
- 会逐步测试公网 IP、域名 HTTP、域名 HTTPS

### 5.3 `production`

表示正式上线阶段。

典型特征：

- 使用正式域名
- 使用正式 HTTPS
- 对外统一提供稳定入口

## 6. 为什么 HTTPS 被放在基础设施层

HTTPS 不属于任何一个业务子系统。

它不回答“用户怎么投票”，也不回答“AI 怎么识别”，而是在回答：

- 请求如何安全进入网关
- 证书如何加载
- 入口协议是 HTTP 还是 HTTPS

所以当前项目把 HTTPS 放进：

- `gateway/app/infra/`

而不是放进：

- `stream`
- `wechat`
- `media`

这符合软件工程里的职责分离原则。

## 7. 当前阅读配置文件的建议顺序

如果你第一次接手这个项目，建议按下面顺序看：

1. `infra/runtime/config.py`  
   先理解环境切换逻辑。

2. `infra/edge/config.py`  
   再理解域名、端口、接入方式。

3. `infra/media_config/config.py`  
   再看媒体层和 SRS 的关系。

4. `infra/auth/config.py`  
   最后看鉴权边界和白名单。

这样不会一上来就被所有配置同时绕晕。

## 7.1 当前版本需要特别说明的配置兼容性事实

为了避免后续读配置时产生误解，当前版本有几项需要明确说明的事实：

### 7.1.1 `jwt_settings` 是当前真实生效的公开认证配置名

虽然认证配置类名是 `AuthSettings`，但当前代码中真正被调用方使用的公开实例名仍然是 `jwt_settings`。这是一项有意保留的向后兼容策略。

因此在当前版本里：

- 配置定义层使用 `AuthSettings` 类
- 调用层继续使用 `jwt_settings`
- 不应在未讨论的情况下直接切换成新的公开实例名

### 7.1.2 `_MOUNTS` 是当前真实生效的静态挂载常量名

`static` 基础设施层当前对外仍使用 `_MOUNTS` 作为静态挂载注册表常量名。这个名字虽然不一定是长期最理想的命名，但它已经被初始化代码真实使用，因此当前版本保持不变。

### 7.1.3 `TLS_PROVIDER` 当前属于说明性字段

三套 `.env` 文件中都保留了 `TLS_PROVIDER`，用于说明当前证书来源，例如 `cloudflare-origin-ca`。但在当前版本中，这个字段还没有直接参与 `gateway` 的启动逻辑。

当前真正决定 HTTPS 启动的是：

- `HTTPS_ENABLED`
- `TLS_CERT_FILE`
- `TLS_KEY_FILE`
- `GATEWAY_INTERNAL_PORT` / `GATEWAY_PORT`

因此可以把 `TLS_PROVIDER` 理解为：

- 当前阶段的说明性字段
- 面向文档与部署认知的字段
- 后续可以再扩展为真正参与策略分支的字段

### 7.1.4 `HTTP_PORT` 当前不是网关启动的直接控制字段

当前 `gateway` 真正启动时读取的是：

- `GATEWAY_HOST`
- `GATEWAY_INTERNAL_PORT`
- `GATEWAY_PORT`
- `HTTPS_ENABLED`

而 Docker 对外端口映射使用的是：

- `GATEWAY_BIND_PORT:GATEWAY_INTERNAL_PORT`

因此 `HTTP_PORT` 在当前版本中更偏向：

- 文档层和接入层说明字段
- 对标准 HTTP 端口语义的表达字段

而不是当前容器启动链路里的唯一控制开关。

## 7.2 当前 docker 到 gateway 的配置兼容性结论

经过本轮核对，当前 Docker 环境文件到 Gateway 配置层的结论如下：

- `APP_ENV`、`APP_RUNTIME_MODE`、`LOCAL_BASE_URL`、`STAGING_BASE_URL`、`PUBLIC_BASE_URL` 与 `runtime/config.py` 对齐
- `DOMAIN_ENABLED`、`HTTPS_ENABLED`、`CLOUDFLARE_ENABLED`、`TLS_CERT_FILE`、`TLS_KEY_FILE` 与 `edge/config.py`、`entrypoint.sh` 对齐
- `GATEWAY_HOST`、`GATEWAY_INTERNAL_PORT`、`GATEWAY_PORT`、`GATEWAY_BIND_PORT` 与 `entrypoint.sh`、`docker-compose.yml` 对齐
- `SRS_HOST`、`SRS_RTMP_PORT`、`SRS_HTTP_PORT`、`SRS_APP`、`SRS_PLAY_PATH_PREFIX`、推流地址字段与 `media_config/config.py` 对齐
- `WECHAT_APPID`、`WECHAT_SECRET` 与 `auth/config.py` 中的微信配置对齐
- `SRS_CALLBACK_TOKEN`、`MEDIA_ADMIN_TOKEN` 与媒体基础设施配置对齐

当前未发现新的“字段名不一致导致运行失败”的 docker -> gateway 配置兼容问题。

需要注意的只有两点：

- `TLS_PROVIDER` 当前仍是说明性字段，不是运行时控制字段
- `HTTP_PORT` 当前仍是说明性/语义性字段，不是启动链路主控字段

## 8. 一句话总结

当前网关配置的核心思路是：

**先由 runtime 决定当前处于什么运行阶段，再由 edge、media、auth 等配置模块分别补充各自职责范围内的行为。**

也就是说：

- `runtime` 决定“现在是谁”
- `edge` 决定“怎么进来”
- `media` 决定“怎么接媒体服务”
- `auth` 决定“谁能访问”
