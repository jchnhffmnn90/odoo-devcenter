#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LD_LIBRARY_PATH="$HOME/.local/usr/lib:$LD_LIBRARY_PATH"
export PATH="$HOME/.local/usr/bin:$HOME/.local/bin:$PATH"

"$DIR/start_postgres.sh"

echo "Starte Odoo 19 auf http://localhost:8069 ..."
"$DIR/venv/bin/python" "$DIR/odoo-19.0/odoo-bin" -c "$DIR/odoo.conf" "$@"
