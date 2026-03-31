#!/bin/sh
set -e
echo "Starting BgUtils POT Provider..."
bgutil-pot server &
exec gunicorn --bind 0.0.0.0:4000 --workers 2 --threads 4 --timeout 1800 app:app
