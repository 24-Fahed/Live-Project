# OBS 推流到服务器教程

本文档对应 `v0.1.2` 的部署方式。

## 1. 当前版本的推流原则

在 `v0.1.2` 中：

- 用户访问 `Admin / API / /live` 可以逐步进入 HTTPS
- 但 OBS 推流继续保持最简单方案：`RTMP + 公网 IP + 独立端口`

也就是说：

- 页面与播放可以走域名、Cloudflare、HTTPS
- OBS 仍然建议直接推到服务器公网 IP 的 `1935` 端口

## 2. 推流地址的组成

OBS 推流通常由两部分组成：

1. 服务器地址
2. 推流码（也可以理解为流名）

当前项目约定：

- 服务器地址：`rtmp://公网IP:1935/live`
- 推流码：例如 `stream-001`

最终推流目标就是：

```text
rtmp://公网IP:1935/live/stream-001
```

## 3. 本地调试时如何填写

### 3.1 服务器地址

```text
rtmp://127.0.0.1:1935/live
```

### 3.2 推流码

```text
stream-001
```

### 3.3 对应播放地址

```text
http://127.0.0.1:8080/live/live/stream-001.m3u8
```

## 4. staging 阶段如何填写

### 4.1 公网 IP + HTTP

服务器地址：

```text
rtmp://公网IP:1935/live
```

推流码：

```text
stream-001
```

播放地址：

```text
http://公网IP:8080/live/live/stream-001.m3u8
```

### 4.2 域名 + HTTP

OBS 推流仍然推荐保持：

```text
rtmp://公网IP:1935/live
```

播放地址则切换为：

```text
http://你的域名/live/live/stream-001.m3u8
```

## 5. prod 阶段如何填写

### 5.1 OBS 推流

正式上线后，OBS 仍然建议填写：

服务器地址：

```text
rtmp://公网IP:1935/live
```

推流码：

```text
stream-001
```

说明：

- RTMP 不走 Cloudflare 代理
- 因此推流入口仍建议使用公网 IP
- 这样最简单、最稳定，也最符合当前项目阶段

### 5.2 用户播放

播放地址切换为：

```text
https://你的域名/live/live/stream-001.m3u8
```

## 6. 管理端的流配置接口

当前项目中，管理员可以通过接口拿到推流地址和播放地址。

例如：

```text
GET /api/v1/admin/media/streams/stream-001
```

典型返回内容会包含：

- `pushUrl`
- `playUrl`
- `publishStatus`

其中：

- `pushUrl` 会根据运行环境返回合适的 RTMP 推流基础地址
- `playUrl` 会根据当前环境自动返回 HTTP 或 HTTPS 的播放地址

## 7. 常见问题

### 7.1 为什么播放可以走 HTTPS，但 OBS 还是走 RTMP + IP？

因为当前项目把 HTTPS 能力放在了 Gateway + Cloudflare 的 HTTP/HTTPS 接入链路里。

但 OBS 推流走的是 RTMP 协议：

- 不经过 Cloudflare 的常规 HTTP/HTTPS 代理
- 不适合直接复用同一套 HTTPS 入口设计

因此在当前阶段，最稳的策略就是：

- 播放走域名 HTTPS
- 推流走公网 IP 的 RTMP 端口

### 7.2 为什么播放地址里是 `/live/live/stream-001.m3u8`？

因为当前播放路径由两部分组成：

1. Gateway 统一暴露的路径前缀：`/live`
2. SRS 的应用名：`live`

拼起来之后就是：

```text
/live/live/stream-001.m3u8
```

这是当前版本的统一设计，不建议在页面里手动拼接其它形式。

### 7.3 如果推流成功但播放失败，应先检查什么？

建议按顺序检查：

1. `live-srs` 是否正常运行
2. `live-gateway` 是否正常运行
3. SRS 是否已经生成 `m3u8` 和分片文件
4. Gateway 的 `/live/...` 代理是否正常
5. 当前访问地址是否与你所处阶段匹配（IP / 域名 / HTTPS）

## 8. 建议的推进顺序

1. 先在 local 跑通 `OBS -> SRS -> Gateway -> 播放`
2. 再在 staging 跑通公网 IP 推流和公网播放
3. 再切到域名回源
4. 最后启用 HTTPS 与 Cloudflare `Full (strict)`

这样推进，协议层问题和业务层问题不会混在一起。
