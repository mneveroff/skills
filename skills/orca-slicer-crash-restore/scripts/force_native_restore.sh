#!/usr/bin/env bash
# Force OrcaSlicer native crash-restore dialog.
# Usage:
#   ./force_native_restore.sh /path/to/safe/copy/of/session_folder
#
# Prerequisites:
#   - Session folder already copied out of temp (this script copies it back into the backup root)
#   - OrcaSlicer fully quit
#   - You understand that a failed restore check can delete last_backup_path

set -euo pipefail

SRC="${1:-}"
if [[ -z "$SRC" || ! -d "$SRC" || ! -f "$SRC/.3mf" ]]; then
  echo "Usage: $0 /path/to/session_folder_with_.3mf" >&2
  exit 1
fi
SRC="$(cd "$SRC" && pwd)"

detect_paths() {
  case "$(uname -s)" in
    Darwin)
      TMP_ROOT="${TMPDIR%/}/orcaslicer_model"
      CONF="${HOME}/Library/Application Support/OrcaSlicer/OrcaSlicer.conf"
      APP_NAME="OrcaSlicer"
      ;;
    Linux)
      TMP_ROOT="/tmp/orcaslicer_model"
      CONF="${HOME}/.config/OrcaSlicer/OrcaSlicer.conf"
      APP_NAME="orca-slicer"
      ;;
    MINGW*|MSYS*|CYGWIN*|Windows_NT)
      echo "Run the equivalent steps on Windows: copy session under %TEMP%\\orcaslicer_model\\, delete lock.txt, set last_backup_path in %APPDATA%\\OrcaSlicer\\OrcaSlicer.conf, launch Orca with no file." >&2
      exit 1
      ;;
    *)
      echo "Unsupported OS: $(uname -s)" >&2
      exit 1
      ;;
  esac
}

detect_paths

DAY="$(date +%a_%b_%d)"   # e.g. Sat_Jul_25 — match Orca's strftime %a_%b_%d
# Prefer keeping the original session folder name if present
BASE="$(basename "$SRC")"
DEST_DAY="${TMP_ROOT}/${DAY}"
DEST="${DEST_DAY}/${BASE}"

echo "Quitting OrcaSlicer..."
if [[ "$(uname -s)" == "Darwin" ]]; then
  osascript -e 'tell application "OrcaSlicer" to quit' >/dev/null 2>&1 || true
  sleep 2
  killall OrcaSlicer >/dev/null 2>&1 || true
else
  killall OrcaSlicer orca-slicer >/dev/null 2>&1 || true
fi
sleep 1

echo "Installing session into ${DEST}"
mkdir -p "$DEST_DAY"
rm -rf "$DEST"
cp -R "$SRC" "$DEST"
rm -f "$DEST/lock.txt"
# Keep origin.txt if present; do not invent one

if [[ ! -f "$CONF" ]]; then
  echo "Config not found: $CONF" >&2
  exit 1
fi

python3 - "$CONF" "$DEST" <<'PY'
import re, sys
from pathlib import Path
conf_path, dest = Path(sys.argv[1]), sys.argv[2]
text = conf_path.read_text(encoding="utf-8")
text2, n = re.subn(r'("last_backup_path"\s*:\s*")[^"]*(")', rf"\1{dest}\2", text, count=1)
if n != 1:
    raise SystemExit(f"Could not patch last_backup_path in {conf_path} (replacements={n})")
conf_path.write_text(text2, encoding="utf-8")
assert not (Path(dest) / "lock.txt").exists()
assert (Path(dest) / ".3mf").exists()
print(f"last_backup_path -> {dest}")
PY

echo "Launching OrcaSlicer with no file..."
if [[ "$(uname -s)" == "Darwin" ]]; then
  open -a "OrcaSlicer"
else
  (orca-slicer >/dev/null 2>&1 &) || (OrcaSlicer >/dev/null 2>&1 &) || true
fi

cat <<'MSG'

Expect dialog: "Previously unsaved items have been detected..."
  -> Restore / Yes
  -> File > Save As immediately

If no dialog: do not open recent files; use build_editable_3mf.py on the safe copy instead.
MSG
