#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LD_LIBRARY_PATH="$HOME/.local/usr/lib:$LD_LIBRARY_PATH"
export PATH="$HOME/.local/usr/bin:$HOME/.local/bin:$PATH"

if pg_isready -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then
    echo "PostgreSQL läuft bereits."
else
    echo "Starte PostgreSQL..."
    pg_ctl -D "$DIR/data/postgres" -l "$DIR/data/postgres/logfile" start
    echo "PostgreSQL erfolgreich gestartet."
fi
