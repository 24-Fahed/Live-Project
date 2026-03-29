# HTTPS 证书目录

`v0.1.2` 开始，网关支持在生产环境直接加载 HTTPS 证书。

请将 Cloudflare Origin CA 证书和私钥放在本目录下：

- `origin.crt`
- `origin.key`

当前默认配置约定：

- 容器内证书路径：`/app/certs/origin.crt`
- 容器内私钥路径：`/app/certs/origin.key`

如果 `HTTPS_ENABLED=true`，但容器内未找到上述文件，`gateway` 启动会直接失败。
这样做是为了尽早暴露配置错误，避免服务器以错误协议对外提供服务。
