# WebSocket 子系统

## 设计模式

观察者模式。维护一个全局客户端连接池，业务子系统调用 `broadcast()` 将消息推送给所有已连接的客户端。客户端按 `data.streamId` 自行过滤消息。

## 构件

| 文件 | 职责 |
|------|------|
| `manager.py` | `ConnectionManager`：管理连接池、注册信息、广播 |
| `handler.py` | `handle_websocket()`：WebSocket 端点处理函数 |

## 接口

| 方法 | 参数 | 说明 |
|------|------|------|
| `ws_manager.connect(ws)` | ws: WebSocket | 接受连接，加入全局连接池 |
| `ws_manager.disconnect(ws)` | ws: WebSocket | 移除连接 |
| `ws_manager.register(ws, info)` | ws: WebSocket, info: dict | 记录客户端注册信息（clientType, userId） |
| `ws_manager.broadcast(message)` | message: dict | 广播消息给所有已连接客户端 |
| `ws_manager.send(ws, message)` | ws: WebSocket, message: dict | 发送消息给指定客户端 |
| `ws_manager.get_total_connections()` | - | 当前连接总数 |
| `ws_manager.get_client_info(ws)` | ws: WebSocket | 获取客户端注册信息 |

## 连接与注册协议

```
1. 客户端连接: ws://host:8080/ws
2. 服务端回复: {"type": "connected", "data": {"message": "已连接到实时数据服务"}}
3. 客户端注册: {"type": "register", "clientType": "miniprogram", "userId": "xxx"}
4. 服务端回复: {"type": "registered", "data": {"message": "注册成功"}}
5. 心跳:     客户端发送 {"type": "ping"} → 服务端回复 {"type": "pong"}
```

## 消息协议

### 服务端 → 客户端

| type | 说明 | data 字段 |
|------|------|-----------|
| `connected` | 连接成功确认 | `{message}` |
| `registered` | 注册成功确认 | `{message}` |
| `votes-updated` | 票数变化 | `{streamId, leftVotes, rightVotes, totalVotes, leftPercentage, rightPercentage}` |
| `liveStatus` | 直播状态变更 | `{isLive, streamUrl, streamId, liveId, startTime}` |
| `newAIContent` | 新AI内容推送 | `{id, content, timestamp, streamId}` |
| `aiStatus` | AI识别状态 | `{status, streamId}` |
| `pong` | 心跳回复 | - |

### 客户端 → 服务端

| type | 说明 |
|------|------|
| `register` | 客户端注册：`{type: "register", clientType: "miniprogram", userId: "xxx"}` |
| `ping` | 心跳请求，服务端回复 `pong` |

## 消息过滤机制

服务端将所有消息广播给全部客户端。每条消息的 `data` 中包含 `streamId` 字段。客户端（小程序）收到消息后，根据当前所在的 streamId 过滤：

```javascript
// 前端过滤逻辑（home.vue）
if (this.streamId && data.streamId && data.streamId !== this.streamId) {
    return; // 忽略不属于当前房间的消息
}
```

## 接入方式

业务子系统导入 `ws_manager` 并调用 `broadcast()`：

```python
from app.comm.ws import ws_manager

await ws_manager.broadcast({
    "type": "votes-updated",
    "data": {"streamId": "room-1", "leftVotes": 100, "rightVotes": 200},
})
```
