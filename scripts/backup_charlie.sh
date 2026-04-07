#!/bin/bash
# Backup Charlie to pCloud
# Run this weekly or before major system changes

set -e

BACKUP_DATE=$(date +%Y-%m-%d)
BACKUP_NAME="charlie-backup-${BACKUP_DATE}.tar.gz"
TEMP_DIR="/tmp/charlie-backup-$$"

echo "🐾 Backing up Charlie..."
echo "Date: ${BACKUP_DATE}"

# Create temp directory
mkdir -p "${TEMP_DIR}"

# Copy everything important
echo "Copying files..."
cp -r ~/.openclaw "${TEMP_DIR}/"

# Copy rclone config if it exists
if [ -d ~/.config/rclone ]; then
    mkdir -p "${TEMP_DIR}/.config/"
    cp -r ~/.config/rclone "${TEMP_DIR}/.config/"
fi

# Copy rclone binary if it exists
if [ -f ~/.local/bin/rclone ]; then
    mkdir -p "${TEMP_DIR}/.local/bin/"
    cp ~/.local/bin/rclone "${TEMP_DIR}/.local/bin/"
fi

# Create archive
echo "Creating archive..."
cd "${TEMP_DIR}"
tar -czf "/tmp/${BACKUP_NAME}" .openclaw $([ -d .config ] && echo .config) $([ -d .local ] && echo .local)

# Generate holographic memory graphs
HM_DIR="/home/damato/.openclaw/workspace/tools/holographic-memory"
echo "🧠 Generating holographic memory graphs..."
python3 "${HM_DIR}/graph.py" --type graph    -o "${HM_DIR}/data/graph.png"
python3 "${HM_DIR}/graph.py" --type sunburst  -o "${HM_DIR}/data/sunburst.png"
python3 "${HM_DIR}/graph.py" --type timeline   -o "${HM_DIR}/data/timeline.png"
echo "✅ Memory graphs refreshed"

# Upload to pCloud
echo "Uploading to pCloud..."
~/.local/bin/rclone mkdir pcloud:/clawd/backups/
~/.local/bin/rclone copy "/tmp/${BACKUP_NAME}" pcloud:/clawd/backups/

# Cleanup
echo "Cleaning up..."
rm -rf "${TEMP_DIR}"
rm "/tmp/${BACKUP_NAME}"

# List backups
echo ""
echo "✅ Backup complete!"
echo ""
echo "Available backups:"
~/.local/bin/rclone ls pcloud:/clawd/backups/ | grep charlie-backup

echo ""
echo "Restore guide: pcloud:/RESTORE_CHARLIE.md"
echo "🐾 Charlie backed up successfully!"
