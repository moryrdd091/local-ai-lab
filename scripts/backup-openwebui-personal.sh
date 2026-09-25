#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# backup-openwebui-personal.sh
#
# Crée une sauvegarde de l'instance Open WebUI personnelle :
#   - compose/personal.compose.yml
#   - data/open-webui-personal
#
# Usage :
#   ./scripts/backup-openwebui-personal.sh
#
# Résultat :
#   Une archive .tar.gz dans backups/ avec la date du jour.
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
ARCHIVE_NAME="openwebui-personal-backup-${TIMESTAMP}.tar.gz"

# Éléments à sauvegarder (chemins relatifs à PROJECT_ROOT)
COMPOSE_FILE="compose/personal.compose.yml"
DATA_DIR="data/open-webui-personal"

# Vérifier que les éléments existent
if [[ ! -f "$PROJECT_ROOT/$COMPOSE_FILE" ]]; then
  echo "ERROR: Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi

if [[ ! -d "$PROJECT_ROOT/$DATA_DIR" ]]; then
  echo "ERROR: Data directory not found: $DATA_DIR" >&2
  exit 1
fi

# Créer le dossier de sauvegarde s'il n'existe pas
mkdir -p "$BACKUP_DIR"

cd "$PROJECT_ROOT"

# Créer l'archive
tar -czf "$BACKUP_DIR/$ARCHIVE_NAME" \
  "$COMPOSE_FILE" \
  "$DATA_DIR"

echo "Backup created: $BACKUP_DIR/$ARCHIVE_NAME"