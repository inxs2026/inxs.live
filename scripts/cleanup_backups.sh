#!/bin/bash
# Auto-backup rotation - keep 4 most recent backups

echo "Cleaning up old backups..."

# Local backups (keep 4, delete 5th and beyond)
ls -t /home/damato/charlie-backup-*.tar.gz 2>/dev/null | tail -n +5 | xargs -r rm -f

# pCloud backups (if mounted)
if [ -d "$HOME/.pcloud" ]; then
    ls -t "$HOME/.pcloud/charlie-backup-*.tar.gz" 2>/dev/null | tail -n +5 | xargs -r rm -f
fi

echo "Cleanup complete - kept 4 most recent backups"
