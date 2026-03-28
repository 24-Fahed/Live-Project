# LIVE Project

一个基于 FastAPI 、微信小程序和 Docker 的直播辩论项目。

## 项目概览

- `frontend/`：微信小程序前端，不参与 Docker 部署
- `gateway/`：FastAPI 网关，提供 API、Admin 静态资源和直播地址代理
- `docker/`：本地、联调、上线的 Docker 编排配置
- `docs/`：架构设计、部署、OBS 推流和面试说明文档

## 当前实现

- 媒体服务使用 `SRS + RTMP 推流 + HLS 播放`
- 播放路径统一为 `/live/...`
- Admin 前端默认跟随当前网关 origin，不再写死 `localhost:8080`
- 国内环境支持可配置镜像源和 PyPI 源
- 小程序前端现在支持 `本地模拟器`、`真机局域网`、`IP 调试`、`IP 上线` 四种运行模式

## 本地 Docker 启动

```bash
cd docker
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

## 本地调试入口

- 健康检查：`http://127.0.0.1:8080/health`
- Admin：`http://127.0.0.1:8080/admin/`
- HLS 播放：`http://127.0.0.1:8080/live/stream-001.m3u8`
- OBS 推流：`rtmp://127.0.0.1:1935/live`
- 推流码：`stream-001`

## 文档导航

- `docs/architecture-design.md`：软件架构设计
- `docs/docker-deployment.md`：Docker 部署说明
- `docs/local-to-production-guide.md`：从本地到上线的教程
- `docs/obs-push-to-server-guide.md`：OBS 推流到服务器教程
- `docs/interviewer-architecture-notes.md`：面试说明与踩坑总结
- `frontend/docs/hbuilderx-run-modes.md`：HBuilderX 运行模式说明

## 已知说明

- 当前前端仍然是 HTTP 访问方案
- 小程序播放 HLS 时如需 HTTPS，需配合 Cloudflare / 网关上线方案
- Windows 下编辑 `.sh`、`.conf`、`.yml`、`.env` 文件时，需保持 `UTF-8 without BOM + LF`
