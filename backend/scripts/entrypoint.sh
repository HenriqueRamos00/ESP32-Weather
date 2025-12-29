#!/bin/sh
set -e

case "$1" in
  migrate)
    alembic upgrade head
    ;;
  serve)
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level warning --proxy-headers --forwarded-allow-ips='*'
    ;;
  *)
    # allow running arbitrary commands too
    exec "$@"
    ;;
esac