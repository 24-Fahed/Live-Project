#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build

echo 'Local debug environment is ready.'
echo 'Gateway: http://127.0.0.1:8080/health'
echo 'Admin:   http://127.0.0.1:8080/admin/'
echo 'Play:    http://127.0.0.1:8080/live/stream-001.m3u8'
echo 'Push:    rtmp://127.0.0.1:1935/live/stream-001'
