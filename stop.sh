#!/usr/bin/env bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LD_LIBRARY_PATH="$HOME/.local/usr/lib:$LD_LIBRARY_PATH"
export PATH="$HOME/.local/usr/bin:$HOME/.local/bin:$PATH"

echo "Stoppe Odoo 19..."
if [ -f "$DIR/odoo.pid" ]; then
    kill "$(cat "$DIR/odoo.pid")" 2>/dev/null || true
    rm -f "$DIR/odoo.pid"
fi
pkill -f "$DIR/odoo-19.0/odoo-bin" 2>/dev/null || true
echo "Odoo 19 gestoppt."

"$DIR/stop_postgres.sh"
