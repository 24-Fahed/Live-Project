# 前端配置文件分析

## 文件位置
`frontend/config/`

## 配置文件结构

### 1. server-mode.js (核心配置 - 前端)
**最重要的配置文件**，控制前端API请求的目标地址。

| 配置项 | 当前值 | 说明 |
|--------|--------|------|
| `USE_MOCK_SERVER` | `true` | 是否使用Mock服务器 |
| `LOCAL_SERVER_URL` | `http://localhost:8080` | 本地网关地址 |
| `MIDDLEWARE_SERVER_URL` | `http://192.168.31.249:8081` | 中间层服务器 |
| `REAL_SERVER_URL` | `http://192.140.160.119:8000` | 真实后端服务器 |
| `API_BASE_URL` | `REAL_SERVER_URL` | **关键配置** - 决定API请求发往哪里 |

**问题**：当前 `API_BASE_URL` 被硬编码为 `REAL_SERVER_URL`，即使 `USE_MOCK_SERVER=true` 也不生效。

### 2. api-config.js (派生配置)
从 `server-mode.js` 导入配置，通过 `getCurrentServerConfig()` 获取URL。
本身不直接定义URL，依赖 `server-mode.js`。

### 3. live-config.js (直播配置)
直播流地址配置，与API请求地址无关。

### 4. server-mode.node.js (后端/Gateway配置)
Node.js后端专用配置，用于gateway服务。与前端配置是独立的。

---

## 修改方案

要让前端流量走本地网关 (localhost:8080)，只需修改 `server-mode.js` 最后一行：

```javascript
// 修改前
export const API_BASE_URL = REAL_SERVER_URL;

// 修改后
export const API_BASE_URL = LOCAL_SERVER_URL;
```

---

## 留档时间
2026-03-17
