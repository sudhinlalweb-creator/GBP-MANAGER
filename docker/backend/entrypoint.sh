#!/usr/bin/env sh
set -eu

if [ "${RUN_DB_MIGRATIONS_ON_START:-true}" = "true" ]; then
  retries="${MIGRATION_MAX_RETRIES:-20}"
  delay="${MIGRATION_RETRY_DELAY_SECONDS:-3}"
  attempt=1

  echo "Running database migrations before API startup..."

  while [ "$attempt" -le "$retries" ]; do
    if alembic upgrade head; then
      echo "Database migrations completed."
      break
    fi

    if [ "$attempt" -eq "$retries" ]; then
      echo "Database migrations failed after ${retries} attempts."
      exit 1
    fi

    echo "Migration attempt ${attempt}/${retries} failed. Retrying in ${delay}s..."
    attempt=$((attempt + 1))
    sleep "$delay"
  done
else
  echo "Skipping database migrations because RUN_DB_MIGRATIONS_ON_START=false."
fi

exec "$@"
