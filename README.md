# LIVE Project v0.1.0

基于 FastAPI 网关、微信小程序前端与 Docker 部署的直播辩论课程项目。

## 项目概览

- `frontend/`：微信小程序前端，发布到微信环境，不参与 Docker 部署。
- `gateway/`：FastAPI 网关，负责 API、Admin 静态资源、媒体地址生成与播放代理。
- `docker/`：本地调试、服务器联调、正式上线三阶段 Docker 配置。
- `docs/`：架构设计、部署说明、OBS 推流教程、面试说明与后续改进方案。

## v0.1.0 当前状态

- 当前媒体链路采用 `SRS + RTMP 推流 + HLS 播放`。
- 网关已经接入独立 `media` 子系统，并统一处理媒体相关接口。
- 播放访问路径已经统一收敛为 `/live/...`，不再保留 `/media/...` 双路径。
- 本地调试和环境切换通过 Docker 配置与 `.env` 文件完成，不需要改业务代码。
- Admin 前端静态资源由 `gateway/static/admin/` 托管。

## 当前实现边界

- 管理端可以配置完整播放地址，并从业务上发起“开始直播”。
- 微信小程序用户登录后，可以根据直播地址请求资源并尝试播放。
- 前端主业务链路当前仍以 `HTTP` 为主。
- 后续全站 `HTTPS`、Cloudflare TLS 接入与更完整媒体层能力，见 `docs/future-plan/未来改进方案.md`。

## 本地 Docker 调试

```bash
cd docker
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

本地常用地址：

- 健康检查：`http://127.0.0.1:8080/health`
- Admin：`http://127.0.0.1:8080/admin/`
- 播放地址：`http://127.0.0.1:8080/live/stream-001.m3u8`
- OBS 推流地址：`rtmp://127.0.0.1:1935/live`
- 推流码示例：`stream-001`

## 仓库结构

```text
Live-Project/
├─ frontend/        微信小程序前端
├─ gateway/         FastAPI 网关与 Admin 静态资源
├─ docker/          Docker 与 SRS 部署配置
├─ docs/            架构、部署、教程与说明文档
├─ stream2/         历史测试与演示资源
└─ 中间文档/         过程性设计资料
```

## 文档导航

- `docs/architecture-design.md`：软件架构设计文档
- `docs/docker-deployment.md`：Docker 部署设计
- `docs/local-to-production-guide.md`：从本地到联调再到上线的完整流程
- `docs/obs-push-to-server-guide.md`：OBS 推流到服务器教程
- `docs/media-infra-upgrade-plan.md`：媒体层与基础设施改造依据
- `docs/interviewer-architecture-notes.md`：给面试官看的架构思路与踩坑总结
- `docs/future-plan/未来改进方案.md`：全站 HTTPS 与未来改进方案

## 已知问题与说明

- 微信小程序模拟器中的播放器不稳定，涉及播放问题时优先以真机测试结果为准。
- 微信开发者工具问题较多，出现异常时先刷新、重启，并确认微信账号已登录。
- 当前版本的媒体层已经从演示型 HLS 方案转向 `SRS`，但仍然是课程项目范围内的简化实现。
- 如果在 Windows 上修改 `.sh`、`.conf`、`.yml`、`.env` 等文件，需要注意 `LF` 与 `UTF-8 without BOM`，否则 Linux 容器可能出现启动问题。

## 版本说明

- `v0.0.1` / `v0.0.2`：仓库早期基础版本
- `v0.1.0`：恢复后的可运行版本，补齐媒体子系统、Docker 三阶段配置、文档体系与 `/live` 单路径播放方案
