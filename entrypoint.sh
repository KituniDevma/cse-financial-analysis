#!/bin/sh

set -e

run_with_log() {
    echo "Starting: $1"
    "$@" || { echo "Failed: $1"; exit 1; }
}

echo "Running data processing scripts..."
run_with_log python /app/backend/scripts/scraper.py
run_with_log python /app/backend/scripts/pdfselector.py
run_with_log python /app/backend/scripts/extractor.py
run_with_log python /app/backend/scripts/dataset.py

echo "Starting backend server..."
cd /app/backend && run_with_log node server.js &

echo "Starting frontend server..."
cd /app/frontend/dashboard/dist && run_with_log npx serve -l 3000 &

sleep 5

if ! pgrep -f "node server.js" > /dev/null; then
    echo "Error: Backend server is not running!"
    exit 1
fi
if ! pgrep -f "npx serve" > /dev/null; then
    echo "Error: Frontend server is not running!"
    exit 1
fi

echo "All services started successfully. Keeping container alive..."
tail -f /dev/null