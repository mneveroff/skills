# OrcaSlicer crash restore — reference

Based on SoftFever/OrcaSlicer (`src/libslic3r/Format/bbs_3mf.cpp`, `src/slic3r/GUI/Plater.cpp`) and community workaround SoftFever/OrcaSlicer#3963.

## How autosave works

- Preference: `backup_switch` + `backup_interval` (seconds) in `OrcaSlicer.conf`.
- Each open project gets a session directory under `orcaslicer_model/<day>/<HH_MM_SS#pid#id>/`.
- Config key `last_backup_path` points at the **current** session folder.
- Meshes are written as per-object files under `3D/Objects/`. Each `*.model` on disk is a **mini zip** whose single entry is the mesh XML path (e.g. `3D/Objects/Part_1.model`).
- The session `.3mf` is a skeleton: metadata, plate layout, and `p:path` references into those object files. It does **not** embed full mesh XML for restore mode.

## Native restore detection (`has_restore_data`)

On editor startup, Plater captures `last_backup_path` and handles `EVT_RESTORE_PROJECT`:

1. If `last_backup_path` is empty → no restore (`origin = "<lock>"`).
2. If `lock.txt` exists and its PID's process name equals the **running** Orca process name → treat as locked (`origin = "<lock>"`), no restore.
3. If `lock.txt` exists and PID parsing throws → **returns false** (no restore).
4. Else require `path/.3mf` to exist.
5. Optionally read `origin.txt`.
6. Rewrite `path` to `path/.3mf` and return true → show restore dialog.

On **Yes**: `load_project(session/.3mf, origin)` with `LoadStrategy::Restore`. The importer opens the skeleton zip; missing object entries are loaded from `backup_path + /3D/Objects/...` on disk (nested zips).

On **No** or failed detection (when origin is not `"<lock>"`): Orca runs `remove_all(last_backup_path)` — **the session is deleted**.

### Practical consequences

- Always copy the session out of temp **before** forcing restore.
- Prefer **deleting** `lock.txt` over rewriting it with a dead PID.
- Set `last_backup_path` **before** launching Orca; Plater captures it at construction.
- Launch with **no file**. Opening the origin project creates a new session and updates `last_backup_path`, so the crash session is never offered.
- Multiple Orca windows / rapid restarts commonly prevent the dialog (new session overwrites the breadcrumb).

## Why hand-zipped “full” 3mf files often fail

| Mistake | Symptom |
|---|---|
| Zipping nested `*.model` zip bytes into a parent 3mf | “Loading of a model file failed” / “no geometry data” |
| Renaming umlaut / Unicode object filenames inconsistently vs `3dmodel.model` / `.rels` | Missing geometry |
| Opening a plate snapshot 3mf | Preview/gcode only; cannot return to editable Prepare model |
| Expecting sibling `3D/` next to a renamed `.3mf` for normal File→Open | Normal open only reads inside the zip |

Correct standalone export: unwrap each nested object zip to raw XML, then zip with UTF-8 names.

## Plate / printer naming

- Files under `Metadata/.PID.N.3mf` are send/slice artifacts (thumbnails + gcode + plate metadata). Useful for reprinting that plate, not for editing assemblies/booleans.
- Bambu device UI may show the project **Title** metadata (e.g. from MakerWorld) rather than the on-disk filename.

## Temp path notes

- macOS: `$TMPDIR` is typically under `/var/folders/.../T/`. Contents can vanish on reboot — copy out early.
- Linux: `/tmp/orcaslicer_model/`.
- Windows: `%TEMP%\orcaslicer_model\`.

## STL extraction

If only meshes are needed: unwrap each nested `*.model` zip, then export **each** `<mesh>` separately with local triangle indices. Concatenating multiple meshes into one STL without index offsets produces spaghetti geometry.

## Config keys

```json
"backup_switch": true,
"backup_interval": "10",
"last_backup_path": "/path/to/orcaslicer_model/.../session_folder"
```

`last_backup_path` must be the **session directory**, not the `.3mf` file inside it.
