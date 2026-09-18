#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export LD_LIBRARY_PATH="$HOME/.local/usr/lib:$LD_LIBRARY_PATH"
export PATH="$HOME/.local/usr/bin:$HOME/.local/bin:$PATH"

"$DIR/start_postgres.sh"

if pgrep -f "$DIR/odoo-19.0/odoo-bin" >/dev/null 2>&1; then
    echo "Odoo 19 läuft bereits im Hintergrund."
else
    echo "Starte Odoo 19 im Hintergrund..."
    nohup "$DIR/venv/bin/python" "$DIR/odoo-19.0/odoo-bin" -c "$DIR/odoo.conf" > "$DIR/odoo.log" 2>&1 &
    echo $! > "$DIR/odoo.pid"
    sleep 2
    if pgrep -f "$DIR/odoo-19.0/odoo-bin" >/dev/null 2>&1; then
        echo "Odoo 19 erfolgreich im Hintergrund gestartet!"
        echo "Erreichbar unter: http://localhost:8069"
        echo "Logs ansehen mit: tail -f odoo.log"
    else
        echo "Fehler beim Starten von Odoo. Siehe odoo.log:"
        cat "$DIR/odoo.log"
    fi
fi
