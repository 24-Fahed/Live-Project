#!/bin/bash
# Docker 部署启动脚本
# 自动启动服务并获取 Cloudflare Tunnel 域名，更新前端配置

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LIVE_CONFIG="$PROJECT_DIR/frontend/config/live-config.js"

cd "$SCRIPT_DIR"

echo "========================================"
echo "  构建并启动 Docker 容器..."
echo "========================================"

docker compose up -d --build

echo ""
echo "等待 Cloudflare Tunnel 启动..."
echo "（首次拉取镜像可能需要几分钟）"

# 等待 tunnel 域名出现（最多 120 秒）
TUNNEL_URL=""
for i in $(seq 1 120); do
    TUNNEL_URL=$(docker compose logs cloudflare 2>/dev/null | grep -oP 'https://[a-z0-9\-]+\.trycloudflare\.com' | tail -1)
    if [ -n "$TUNNEL_URL" ]; then
        break
    fi
    sleep 1
    # 每 10 秒打印一次进度
    if [ $((i % 10)) -eq 0 ]; then
        echo "  已等待 ${i} 秒..."
    fi
done

if [ -z "$TUNNEL_URL" ]; then
    echo ""
    echo "错误: Cloudflare Tunnel 未能在 120 秒内启动"
    echo "请手动查看日志: docker compose logs cloudflare"
    exit 1
fi

echo "  Tunnel 域名: $TUNNEL_URL"

# 自动更新前端配置
if [ -f "$LIVE_CONFIG" ]; then
    sed -i "s|https://<TUNNEL_DOMAIN>|$TUNNEL_URL|g" "$LIVE_CONFIG"
    echo ""
    echo "已自动更新 frontend/config/live-config.js"
else
    echo ""
    echo "警告: 未找到 $LIVE_CONFIG，请手动替换 <TUNNEL_DOMAIN>"
fi

echo ""
echo "========================================"
echo "  部署完成"
echo "========================================"
echo ""
echo "  API (HTTP):   http://192.168.137.1:8080"
echo "  HLS (HTTPS):  $TUNNEL_URL/hls/stream-001/stream-001.m3u8"
echo ""
echo "  手机访问流程:"
echo "    1. 手机连接电脑热点"
echo "    2. 微信真机调试 -> API 走 http://192.168.137.1:8080"
echo "    3. HLS 播放走 $TUNNEL_URL"
echo ""
echo "  查看日志:     docker compose logs -f"
echo "  停止服务:     ./stop.sh"
echo ""
