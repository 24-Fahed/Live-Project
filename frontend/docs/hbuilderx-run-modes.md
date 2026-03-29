# HBuilderX 运行模式说明

## 1. 本地模拟器

- 标识：默认 `mp-weixin`
- 地址：`http://localhost:8080`
- 适用阶段：本地业务联调

## 2. 真机局域网调试

- 标识：`mp-weixin-device`
- 地址：`http://192.168.137.1:8080`
- 适用阶段：同一局域网内真机调试

## 3. 公网 IP 调试

- 标识：`mp-weixin-ip-debug`
- 地址：`http://106.14.254.19:8080`
- 适用阶段：`staging` 第一阶段，验证公网 IP 与 HTTP 能力

## 4. 公网 IP 上线联调

- 标识：`mp-weixin-ip-release`
- 地址：`http://106.14.254.19:8080`
- 适用阶段：保留的 IP 模式，用于回归检查与应急定位

## 5. 域名 HTTP 联调

- 标识：`mp-weixin-domain-staging`
- 地址：`http://24fahed.cn`
- 适用阶段：`staging` 第二阶段，验证域名与回源是否正常

## 6. 域名 HTTPS 上线

- 标识：`mp-weixin-domain-prod`
- 地址：`https://24fahed.cn`
- 适用阶段：`prod` 正式运行模式
- WebSocket：同域自动切换为 `wss://24fahed.cn/ws`

## 7. 使用建议

建议按下面的顺序推进：

1. 先在本地用 `mp-weixin` 验证业务逻辑
2. 再切到 `mp-weixin-ip-debug` 验证公网 IP HTTP 能力
3. 再切到 `mp-weixin-domain-staging` 验证域名 HTTP 回源
4. 最后切到 `mp-weixin-domain-prod` 验证 HTTPS / WSS 与 Cloudflare
