#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LD_LIBRARY_PATH="$HOME/.local/usr/lib:$LD_LIBRARY_PATH"
export PATH="$HOME/.local/usr/bin:$HOME/.local/bin:$PATH"

echo "=== Status Prüfung ==="

if pg_isready -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then
    echo "[✓] PostgreSQL: Läuft (Port 5432)"
else
    echo "[✗] PostgreSQL: Läuft NICHT"
fi

if pgrep -f "$DIR/odoo-19.0/odoo-bin" >/dev/null 2>&1; then
    echo "[✓] Odoo 19:    Läuft (Port 8069)"
    echo "    URL: http://localhost:8069 oder http://127.0.0.1:8069"
else
    echo "[✗] Odoo 19:    Läuft NICHT"
fi
