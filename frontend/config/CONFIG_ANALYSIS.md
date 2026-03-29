# 前端配置文件分析

## 1. 当前运行模式

| 模式 | 适用阶段 | 地址 | WebSocket 方案 |
| --- | --- | --- | --- |
| 本地模拟器 | local | `http://localhost:8080` | `ws://localhost:8080/ws` |
| 真机局域网调试 | local | `http://192.168.137.1:8080` | `ws://192.168.137.1:8080/ws` |
| 公网 IP 调试 | staging 第一步 | `http://106.14.254.19:8080` | `ws://106.14.254.19:8080/ws` |
| 域名 HTTP 联调 | staging 第二步 | `http://24fahed.cn` | `ws://24fahed.cn/ws` |
| 域名 HTTPS 上线 | prod | `https://24fahed.cn` | `wss://24fahed.cn/ws` |

## 2. 配置职责

`frontend/config/server-mode.js` 负责统一定义不同运行模式下的基础地址。

该文件承担的职责是：

- 决定小程序当前使用哪一个 API 基础地址
- 让 WebSocket 地址跟随 `http/https` 自动切换为 `ws/wss`
- 把本地、IP 调试、域名联调、正式 HTTPS 上线等模式集中管理
- 避免在页面业务代码中散落硬编码地址

## 3. v0.1.2 的改动方向

`v0.1.2` 之后，前端运行模式不再只区分“本地 / 真机 / 公网 IP”，而是进一步覆盖：

- `staging` 的公网 IP 测试
- `staging` 的域名 HTTP 联调
- `prod` 的域名 HTTPS 上线

这与当前整体部署策略保持一致：

1. `local` 主要验证业务逻辑与基础联调
2. `staging` 作为公网集成测试环境，逐步验证 IP、域名、HTTPS 与 Cloudflare
3. `prod` 统一收口到 HTTPS / WSS

## 4. 建议保持的工程原则

- 页面代码只依赖 `API_BASE_URL` 与统一的 WebSocket 构造方法
- 地址切换只在配置文件中发生，不直接修改业务页面逻辑
- 生产环境统一走 `https + wss`
- 旧的 IP 模式继续保留，用于公网回归与问题定位
