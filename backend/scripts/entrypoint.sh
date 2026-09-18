#!/bin/sh
set -e

until alembic upgrade head; do
  echo "database not ready, retrying in 2s..."
  sleep 2
done

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
