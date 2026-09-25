#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
ARCHIVE_NAME="openwebui-shared-backup-${TIMESTAMP}.tar.gz"

COMPOSE_FILE="compose/shared.compose.yml"
DATA_DIR="data/open-webui-shared"

if [[ ! -f "$PROJECT_ROOT/$COMPOSE_FILE" ]]; then
  echo "ERROR: Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_ROOT/$DATA_DIR" ]]; then
  echo "ERROR: Data directory not found: $DATA_DIR" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"

cd "$PROJECT_ROOT"

tar -czf "$BACKUP_DIR/$ARCHIVE_NAME" \
  "$COMPOSE_FILE" \
  "$DATA_DIR"

echo "Backup created: $BACKUP_DIR/$ARCHIVE_NAME"