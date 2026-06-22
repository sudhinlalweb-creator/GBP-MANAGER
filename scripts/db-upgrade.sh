#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/../backend"

alembic_bin="$(python3 -m site --user-base)/bin/alembic"

if [ -x "$alembic_bin" ]; then
  exec "$alembic_bin" upgrade head
fi

exec alembic upgrade head
