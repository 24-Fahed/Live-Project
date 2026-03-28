#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

docker compose --env-file .env.staging -f docker-compose.yml -f docker-compose.staging.yml up -d --build
