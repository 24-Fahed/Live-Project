# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

直播辩论系统，包含小程序前端、网关服务和后台管理界面。

## 常用命令

### Gateway 网关服务
```bash
cd gateway
npm install          # 安装依赖
npm start            # 生产模式启动
npm run dev          # 开发模式 (nodemon)
./gateway.ps1 start  # PowerShell: 后台启动
./gateway.ps1 stop   # PowerShell: 停止服务
./gateway.ps1 status # PowerShell: 查看状态
```

### Frontend 前端项目
```bash
cd frontend
npm install          # 安装依赖
npm run dev:mp-weixin  # 微信小程序开发模式
npm run build:mp-weixin # 微信小程序生产构建
npm run dev:h5       # H5 开发模式
npm run swagger      # 启动 Swagger API 文档服务
```

## 架构说明

```
┌─────────────────┐
│  小程序客户端    │
│  (uni-app)      │
└────────┬────────┘
         │ WebSocket (/ws)
         ▼
┌─────────────────┐
│  Gateway        │  端口: 8080
│  (gateway.js)   │
├─────────────────┤
│ /api/*   → API 路由处理
│ /admin   → 后台管理页面
│ /ws      → WebSocket 实时通信
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  admin/         │  后台管理模块
│  data/          │  JSON 数据存储
└─────────────────┘
```

### 模块依赖关系

Gateway 运行需要以下目录（从 frontend 复制）：
- `admin/` - 后台管理模块，包含 db.js (数据库操作)、admin-api.js、admin.js 等
- `data/` - 数据文件存储 (streams.json, users.json, debate.json 等)

### WebSocket 消息类型

| 类型 | 用途 |
|------|------|
| `liveStatus` | 直播状态更新 |
| `votes-updated` | 投票数据更新 |
| `aiStatus` | AI 识别状态 |
| `newAIContent` | 新 AI 内容推送 |
| `debate-updated` | 辩题更新 |
| `connected` | 连接成功确认 |

### 关键文件

- `gateway/gateway.js` - 网关主服务，处理 API、WebSocket、静态资源
- `gateway/config/server-mode.node.js` - 服务器配置（端口、地址）
- `frontend/server.js` - 前端内嵌服务器（与 gateway 功能重叠）
- `frontend/admin/db.js` - 数据库/JSON 文件操作模块
- `frontend/pages/` - 小程序页面组件
- `frontend/config/` - 前端配置文件

## 配置修改

修改服务器地址时，编辑 `gateway/config/server-mode.node.js`：
```javascript
const REAL_SERVER_URL = 'http://YOUR_SERVER_IP:8080';
const REAL_SERVER_PORT = 8080;
```
