# LIVE Project

一个基于 FastAPI、微信小程序、SRS 与 Docker 的直播辩论项目。

## 项目概览

- `frontend/`：微信小程序前端，独立发布到微信，不参与 Docker 部署
- `gateway/`：FastAPI 网关，统一承载 API、Admin 静态资源、`/live` 播放代理与 WebSocket
- `docker/`：本地、staging、prod 三阶段部署编排与环境变量模板
- `docs/`：架构设计、部署教程、API 文档、OBS 推流说明与版本规划文档

## 当前版本

当前主线版本目标已经推进到 `v0.1.2` 设计阶段，重点补齐：

- Cloudflare + Gateway 的 HTTPS 接入能力
- WebSocket 向 `WSS` 的联动能力
- `local -> staging -> prod` 的递进式公网集成测试策略
- 项目级 RESTful API 文档

## 当前实现边界

- 媒体服务使用 `SRS + RTMP 推流 + HLS 播放`
- 播放入口统一由 Gateway 暴露为 `/live/...`
- 当前 HLS 访问路径实际为：`/live/{stream_id}.m3u8`
- Admin 前端资源由 Gateway 托管
- 微信小程序前端通过运行模式切换本地、IP、域名与 HTTPS 入口
- OBS 继续通过公网 IP 的 `1935` 端口推流，不走 Cloudflare 代理

## 本地启动

```bash
cd docker
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

## 本地调试入口

- 健康检查：`http://127.0.0.1:8080/health`
- Admin：`http://127.0.0.1:8080/admin/`
- HLS 播放：`http://127.0.0.1:8080/live/stream-001.m3u8`
- WebSocket：`ws://127.0.0.1:8080/ws`
- OBS 推流：`rtmp://127.0.0.1:1935/live`
- 推流码：`stream-001`

## 文档导航

- `docs/architecture-design.md`：软件架构设计文档
- `docs/docker-deployment.md`：Docker 部署结构说明
- `docs/local-to-production-guide.md`：从本地到上线的环境切换与操作教程
- `docs/obs-push-to-server-guide.md`：OBS 推流到服务器教程
- `docs/api-reference.md`：项目级 RESTful API 文档
- `docs/gateway-config-guide.md`：网关配置说明文档
- `docs/interviewer-architecture-notes.md`：面试官说明与踩坑总结
- `docs/v0.1.2/v0.1.2-planning-draft.md`：`v0.1.2` 版本规划草案
- `frontend/docs/hbuilderx-run-modes.md`：HBuilderX 运行模式说明

## 更新日志

### v0.1.2（规划与实现中）

- 将 HTTPS 明确归类为网关基础设施能力，而不是业务子系统
- 确定 `staging` 为公网集成测试环境，按“公网 IP -> 域名 HTTP -> 域名 HTTPS”逐步开启能力
- 规划并落入配置模型的 `WSS` 联动能力
- 三套 `.env` 调整为按分组组织，并补入 HTTPS / TLS / Cloudflare 开关
- 新增项目级 API 文档：`docs/api-reference.md`
- HBuilderX 运行模式扩展到域名 HTTP 联调和域名 HTTPS 上线

### v0.1.1

- 适配国内部署环境，补入国内镜像源与 PyPI 源配置
- 修复 Docker 拉取基础镜像与安装依赖时的国内网络问题

### v0.1.0

- 完成 `gateway + srs` 的基础部署形态
- 统一 `/live` 媒体播放代理入口
- 增加本地、staging、prod 的基础 Docker 环境方案

## 已知说明

- `prod` 目标是统一收口到 `HTTPS + WSS`
- `staging` 阶段允许按能力增量测试 HTTP / 域名 / HTTPS，不等同于正式上线入口
- Windows 下编辑 `.sh`、`.conf`、`.yml`、`.env` 文件时，仍需保持 `UTF-8 without BOM + LF`
