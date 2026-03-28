# 前端配置文件分析

## 当前结论

当前前端仍然可以本地运行。

## 运行模式

| 档位 | 说明 | 地址 |
| --- | --- | --- |
| 本地模拟器 | 微信开发者工具默认运行 | `http://localhost:8080` |
| 真机局域网 | 手机与开发机在同一局域网 | `http://192.168.137.1:8080` |
| IP 调试 | 通过公网 IP 联调 | `http://106.14.254.19:8080` |
| IP 上线 | 通过公网 IP 对外提供服务 | `http://106.14.254.19:8080` |

## HBuilderX 入口

- `mp-weixin-device`：真机局域网调试
- `mp-weixin-ip-debug`：IP 调试
- `mp-weixin-ip-release`：IP 上线

## 维护规则

如果地址发生变化，只需修改 `frontend/config/server-mode.js` 中的 `REAL_DEVICE_SERVER_URL` 和 `PUBLIC_IP_SERVER_URL`。
