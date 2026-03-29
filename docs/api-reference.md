# v0.1.2 API 接口说明

本文档按 RESTful 风格整理当前网关已经提供的主要接口，作为 `v0.1.2` 阶段的接口级说明。

## 1. 统一约定

### 1.1 基础入口

- local：`http://127.0.0.1:8080`
- staging（公网 IP / HTTP）：`http://公网IP:8080`
- staging（域名 / HTTP）：`http://域名`
- prod（域名 / HTTPS）：`https://域名`

### 1.2 WebSocket

- HTTP 环境：`ws://host/ws`
- HTTPS 环境：`wss://host/ws`

### 1.3 统一响应格式

当前项目大部分接口采用如下风格：

```json
{
  "success": true,
  "data": {}
}
```

失败时通常返回：

```json
{
  "success": false,
  "message": "error message"
}
```

### 1.4 鉴权边界

以下入口默认在白名单中，可直接访问：

- `/api/wechat-login`
- `/health`
- `/ws`
- `/live/...`
- `/admin` 与静态资源入口

其余管理接口默认受网关鉴权控制。

## 2. 健康检查与实时通信

### 2.1 健康检查

- 方法：`GET`
- 路径：`/health`
- 说明：检查网关是否正常运行

### 2.2 WebSocket

- 协议：`WS / WSS`
- 路径：`/ws`
- 说明：用于实时推送直播状态、投票变化、AI 状态等消息

## 3. 微信登录接口

### 3.1 微信登录

- 方法：`POST`
- 路径：`/api/wechat-login`
- 说明：小程序使用微信登录 code 换取用户身份与业务令牌

请求体示例：

```json
{
  "code": "wx-login-code",
  "userInfo": {
    "nickName": "用户昵称"
  }
}
```

## 4. 用户侧直播与互动接口

### 4.1 获取辩题

- 方法：`GET`
- 路径：`/api/v1/debate-topic`
- 查询参数：`stream_id`
- 说明：获取当前直播流关联的辩题信息

### 4.2 获取投票结果

- 方法：`GET`
- 路径：`/api/v1/votes`
- 查询参数：`stream_id`
- 说明：获取当前直播流的正反方票数

### 4.3 用户投票

- 方法：`POST`
- 路径：`/api/v1/user-vote`
- 说明：用户提交一次投票分布

请求体示例：

```json
{
  "streamId": "stream-001",
  "leftVotes": 60,
  "rightVotes": 40
}
```

### 4.4 获取 AI 内容列表

- 方法：`GET`
- 路径：`/api/v1/ai-content`
- 查询参数：`stream_id`
- 说明：获取当前直播流可展示的 AI 内容

### 4.5 添加评论

- 方法：`POST`
- 路径：`/api/v1/comment`
- 说明：给 AI 内容添加评论

### 4.6 删除评论

- 方法：`DELETE`
- 路径：`/api/v1/comment/{comment_id}`
- 说明：删除指定评论

### 4.7 点赞内容或评论

- 方法：`POST`
- 路径：`/api/v1/like`
- 说明：对 AI 内容或评论点赞

## 5. 管理端直播与流管理接口

### 5.1 获取直播流列表

- 方法：`GET`
- 路径：`/api/v1/admin/streams`
- 说明：获取当前已配置的直播流列表

### 5.2 创建直播流

- 方法：`POST`
- 路径：`/api/v1/admin/streams`
- 说明：新增一条直播流配置

### 5.3 更新直播流

- 方法：`PUT`
- 路径：`/api/v1/admin/streams/{stream_id}`
- 说明：更新直播流基础信息

### 5.4 删除直播流

- 方法：`DELETE`
- 路径：`/api/v1/admin/streams/{stream_id}`
- 说明：删除直播流

### 5.5 开始直播

- 方法：`POST`
- 路径：`/api/v1/admin/live/start`
- 说明：将指定直播流标记为开始直播

### 5.6 停止直播

- 方法：`POST`
- 路径：`/api/v1/admin/live/stop`
- 说明：将指定直播流标记为停止直播

### 5.7 获取直播状态

- 方法：`GET`
- 路径：`/api/v1/admin/live/status`
- 查询参数：`stream_id`
- 说明：查询直播状态

### 5.8 广播观看人数

- 方法：`POST`
- 路径：`/api/v1/admin/live/broadcast-viewers`
- 查询参数：`stream_id`
- 说明：手动广播指定直播流的观看人数

## 6. 管理端投票与统计接口

### 6.1 管理端查看票数

- 方法：`GET`
- 路径：`/api/v1/admin/votes`
- 查询参数：`stream_id`

### 6.2 管理端设置票数

- 方法：`PUT`
- 路径：`/api/v1/admin/votes`

### 6.3 管理端重置票数

- 方法：`POST`
- 路径：`/api/v1/admin/votes/reset`

### 6.4 直播中增量更新票数

- 方法：`POST`
- 路径：`/api/v1/admin/live/update-votes`

### 6.5 直播中重置票数

- 方法：`POST`
- 路径：`/api/v1/admin/live/reset-votes`

### 6.6 Dashboard 数据

- 方法：`GET`
- 路径：`/api/v1/admin/dashboard`
- 查询参数：`stream_id`

### 6.7 观看人数统计

- 方法：`GET`
- 路径：`/api/v1/admin/live/viewers`
- 查询参数：`stream_id`

### 6.8 投票统计

- 方法：`GET`
- 路径：`/api/v1/admin/statistics/votes`
- 查询参数：`stream_id`

### 6.9 用户列表

- 方法：`GET`
- 路径：`/api/v1/admin/users`
- 查询参数：分页参数

## 7. 管理端辩题、流程与评委接口

### 7.1 创建辩题

- 方法：`POST`
- 路径：`/api/v1/admin/debates`

### 7.2 获取辩题详情

- 方法：`GET`
- 路径：`/api/v1/admin/debates/{debate_id}`

### 7.3 更新辩题

- 方法：`PUT`
- 路径：`/api/v1/admin/debates/{debate_id}`

### 7.4 获取直播流关联辩题

- 方法：`GET`
- 路径：`/api/v1/admin/streams/{stream_id}/debate`

### 7.5 关联直播流与辩题

- 方法：`PUT`
- 路径：`/api/v1/admin/streams/{stream_id}/debate`

### 7.6 解除直播流与辩题关联

- 方法：`DELETE`
- 路径：`/api/v1/admin/streams/{stream_id}/debate`

### 7.7 获取辩论流程

- 方法：`GET`
- 路径：`/api/v1/admin/debate-flow`
- 查询参数：`stream_id`

### 7.8 保存辩论流程

- 方法：`POST`
- 路径：`/api/v1/admin/debate-flow`

### 7.9 控制辩论流程

- 方法：`POST`
- 路径：`/api/v1/admin/debate-flow/control`

### 7.10 获取评委配置

- 方法：`GET`
- 路径：`/api/v1/admin/judges`
- 查询参数：`stream_id`

### 7.11 保存评委配置

- 方法：`POST`
- 路径：`/api/v1/admin/judges`

## 8. 管理端 AI 内容接口

### 8.1 获取 AI 内容列表

- 方法：`GET`
- 路径：`/api/v1/admin/ai-content/list`

### 8.2 获取 AI 内容详情

- 方法：`GET`
- 路径：`/api/v1/admin/ai-content/{content_id}`

### 8.3 删除 AI 内容

- 方法：`DELETE`
- 路径：`/api/v1/admin/ai-content/{content_id}`

### 8.4 获取 AI 内容评论

- 方法：`GET`
- 路径：`/api/v1/admin/ai-content/{content_id}/comments`

### 8.5 删除 AI 内容评论

- 方法：`DELETE`
- 路径：`/api/v1/admin/ai-content/{content_id}/comments/{comment_id}`

### 8.6 启动 AI

- 方法：`POST`
- 路径：`/api/v1/admin/ai/start`

### 8.7 停止 AI

- 方法：`POST`
- 路径：`/api/v1/admin/ai/stop`

### 8.8 切换 AI 状态

- 方法：`POST`
- 路径：`/api/v1/admin/ai/toggle`

## 9. 媒体层接口

### 9.1 获取推流配置

- 方法：`GET`
- 路径：`/api/v1/admin/media/push-config`
- 查询参数：`stream_id`
- 说明：返回推流地址、播放地址及当前流状态

### 9.2 获取指定流媒体信息

- 方法：`GET`
- 路径：`/api/v1/admin/media/streams/{stream_id}`

### 9.3 获取播放地址

- 方法：`GET`
- 路径：`/api/v1/media/play-url`
- 查询参数：`stream_id`

### 9.4 接收媒体服务器回调

- 方法：`POST`
- 路径：`/api/v1/internal/media/hooks/{event_name}`
- 说明：SRS 通过回调更新推流状态

## 10. 直播播放入口

### 10.1 HLS 播放地址

- 方法：`GET`
- 路径：`/live/{app}/{stream_id}.m3u8`
- 示例：`/live/live/stream-001.m3u8`
- 说明：统一经由 gateway 对外暴露的 HLS 播放入口

### 10.2 HLS 分片地址

- 方法：`GET`
- 路径：`/live/{app}/{segment}`
- 说明：播放清单引用的 `.ts` 分片同样经由 gateway 代理

## 11. 说明

- `v0.1.2` 目标是将 `Admin / API / /live / WebSocket` 全部纳入 HTTPS / WSS 统一入口。
- `staging` 允许按步骤验证公网 IP、域名和 HTTPS；`prod` 统一收口到 HTTPS。
- 后续如接口继续扩展，应优先保持现有 RESTful 风格与统一响应格式，避免在小版本中引入新的混杂协议习惯。
