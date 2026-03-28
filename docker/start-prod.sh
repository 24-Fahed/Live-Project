#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build
