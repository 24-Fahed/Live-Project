#!/bin/bash
set -e

# 启动 HLS 服务器 (HTTPS, 端口 8443) - 后台运行
python -m app.subsystems.hls.script.hls_server start &
HLS_PID=$!

# 启动主网关 (HTTP, 端口 8080) - 前台运行
uvicorn app.main:app --host 0.0.0.0 --port 8080

# 网关退出后清理 HLS 进程
kill $HLS_PID 2>/dev/null
