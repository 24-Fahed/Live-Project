#!/bin/bash
set -e

HOST="${GATEWAY_HOST:-0.0.0.0}"
PORT="${GATEWAY_INTERNAL_PORT:-${GATEWAY_PORT:-8080}}"
HTTPS_ENABLED_VALUE="${HTTPS_ENABLED:-false}"

UVICORN_ARGS=(
  app.main:app
  --host "$HOST"
  --port "$PORT"
  --proxy-headers
  --forwarded-allow-ips="*"
)

if [ "$HTTPS_ENABLED_VALUE" = "true" ]; then
  CERT_FILE="${TLS_CERT_FILE:-/app/certs/origin.crt}"
  KEY_FILE="${TLS_KEY_FILE:-/app/certs/origin.key}"

  if [ ! -f "$CERT_FILE" ]; then
    echo "[entrypoint] HTTPS is enabled but certificate file was not found: $CERT_FILE" >&2
    exit 1
  fi

  if [ ! -f "$KEY_FILE" ]; then
    echo "[entrypoint] HTTPS is enabled but key file was not found: $KEY_FILE" >&2
    exit 1
  fi

  UVICORN_ARGS+=(
    --ssl-certfile "$CERT_FILE"
    --ssl-keyfile "$KEY_FILE"
  )
fi

exec uvicorn "${UVICORN_ARGS[@]}"
