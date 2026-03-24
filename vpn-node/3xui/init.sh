#!/bin/bash

DB_PATH="/etc/x-ui/x-ui.db"

/usr/local/bin/x-ui &
XUI_PID=$!

echo "Waiting for database initialization..."
RETRY=0
while [ $RETRY -lt 10 ]; do
    if [ -f "$DB_PATH" ]; then
        TABLE_EXISTS=$(sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE type='table' AND name='settings';")
        if [ "$TABLE_EXISTS" == "settings" ]; then
            break
        fi
    fi
    sleep 2
    RETRY=$((RETRY+1))
done

kill $XUI_PID
sleep 2

echo "Applying custom settings from ENV..."

sqlite3 "$DB_PATH" <<EOF
INSERT OR REPLACE INTO settings (key, value) VALUES ('webPort', '${XUI_PORT}');
INSERT OR REPLACE INTO settings (key, value) VALUES ('webBasePath', '/${XUI_PATH}/');
UPDATE users SET username='${XUI_LOGIN}', password='${XUI_PASS}' WHERE id=1;
EOF

echo "Settings applied. Starting 3x-ui in foreground..."

exec /usr/local/bin/x-ui