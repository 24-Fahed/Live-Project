#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo 'Stopping containers...'
docker compose down

echo 'Stopped.'
