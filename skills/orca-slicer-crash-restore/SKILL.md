---
name: orca-slicer-crash-restore
description: Recover unsaved OrcaSlicer projects from crash autosave backups, including native restore and rebuilding an editable 3mf. Use when OrcaSlicer crashed, a project was lost, restore dialog did not appear, or the user asks to recover a 3mf/gcode.3mf/plate from orcaslicer_model backups.
---

# OrcaSlicer crash restore

Recover work that existed only in Orca's autosave, not on disk.

## Safety first

1. **Copy the backup folder before touching anything.** If restore detection fails, Orca **deletes** `last_backup_path`.
2. Quit **all** Orca windows. Do not Save / Don't Save over the lost work.
3. Do **not** open the original project from Recent Files until restore is done — that creates a new empty session and overwrites `last_backup_path`.

## Locate the backup

Autosave lives under the OS temp dir, not Application Support:

| OS | Backup root | Config |
|---|---|---|
| macOS | `$TMPDIR/orcaslicer_model/` | `~/Library/Application Support/OrcaSlicer/OrcaSlicer.conf` |
| Linux | `/tmp/orcaslicer_model/` | `~/.config/OrcaSlicer/OrcaSlicer.conf` |
| Windows | `%TEMP%\orcaslicer_model\` | `%APPDATA%\OrcaSlicer\OrcaSlicer.conf` |

Session folders look like `DayName/HH_MM_SS#PID#id/` and contain:

- `.3mf` — skeleton project (settings + object references)
- `3D/Objects/*.model` — **nested zip** files with mesh XML
- `origin.txt` — path of the file the session was based on
- `lock.txt` — PID of the Orca process that owned the session
- `Metadata/.PID.N.3mf` / `.gcode` — plate send/slice snapshots

Pick the session whose `origin.txt` / object timestamps match the lost work (usually the largest recent folder with a populated `3D/Objects/`).

## Preferred path: native restore

Orca only restores via startup check (`has_restore_data` → restore dialog), not by opening a hand-built zip.

1. Copy the session folder to a safe location outside temp.
2. Re-place it under the backup root (same layout is fine).
3. **Delete `lock.txt`** (do not write a dead PID — that can make detection fail).
4. Ensure `.3mf` and `origin.txt` exist.
5. With Orca fully quit, set config `"last_backup_path"` to that session folder path.
6. Launch Orca **with no file**. Expect: *Previously unsaved items have been detected…* → restore.
7. **Save As** immediately to a durable path.

Use [scripts/force_native_restore.sh](scripts/force_native_restore.sh) for steps 2–6.

## Fallback: rebuild an editable 3mf

If the dialog never appears, build a normal project file:

1. Unzip the session `.3mf` skeleton.
2. For each `3D/Objects/*.model`, open it as a zip and extract the inner `.model` **XML** (do not embed the nested zip bytes).
3. Copy `Auxiliaries/` and plate assets from `Metadata/` / plate snapshots as needed.
4. Clear absolute `gcode_file` paths that point into temp.
5. Zip with UTF-8 entry names → open in Orca → Save As.

Use [scripts/build_editable_3mf.py](scripts/build_editable_3mf.py).

## Do not confuse these

- **Plate snapshot** (`Metadata/.PID.N.3mf`): sliced plate + gcode only; not an editable project.
- **Printer job title**: often from 3mf metadata `Title`, not the filename on disk.
- **Opening `origin.txt`'s file alone**: loads the last **saved** version, not the autosave.

## Details

Source-backed restore rules, failure modes, and STL notes: [REFERENCE.md](REFERENCE.md).
