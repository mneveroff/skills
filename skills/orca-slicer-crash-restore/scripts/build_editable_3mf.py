#!/usr/bin/env python3
"""Rebuild a normal editable OrcaSlicer/Bambu .3mf from a crash autosave session.

Session layout (input dir):
  .3mf                 skeleton
  3D/Objects/*.model   nested zip files containing mesh XML
  Auxiliaries/         optional
  Metadata/            optional plate snapshots

Usage:
  python3 build_editable_3mf.py /path/to/session_folder [/path/to/out.3mf]
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import zipfile
from pathlib import Path


def unwrap_model(path: Path) -> bytes:
    data = path.read_bytes()
    if data[:2] != b"PK":
        return data
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        preferred = [n for n in names if n.endswith(path.name)]
        pick = preferred[0] if preferred else next(n for n in names if n.endswith(".model"))
        return zf.read(pick)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    src = Path(sys.argv[1]).expanduser().resolve()
    out = (
        Path(sys.argv[2]).expanduser().resolve()
        if len(sys.argv) > 2
        else src.parent / f"{src.name}_recovered_editable.3mf"
    )
    skeleton = src / ".3mf"
    objects = src / "3D" / "Objects"
    if not skeleton.is_file() or not objects.is_dir():
        print(f"Not a session folder (need .3mf and 3D/Objects): {src}", file=sys.stderr)
        return 1

    work = src.parent / f".{src.name}_rebuild_work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    with zipfile.ZipFile(skeleton) as zf:
        zf.extractall(work)

    dst_objects = work / "3D" / "Objects"
    dst_objects.mkdir(parents=True, exist_ok=True)
    for model in objects.glob("*.model"):
        (dst_objects / model.name).write_bytes(unwrap_model(model))

    aux = src / "Auxiliaries"
    if aux.is_dir():
        shutil.copytree(aux, work / "Auxiliaries", dirs_exist_ok=True)

    # Prefer newest plate snapshot assets if present
    snaps = sorted((src / "Metadata").glob(".*.3mf")) if (src / "Metadata").is_dir() else []
    if snaps:
        with zipfile.ZipFile(snaps[-1]) as zf:
            for name in zf.namelist():
                if name.startswith("Metadata/") and name.rsplit(".", 1)[-1] in {
                    "png",
                    "json",
                    "gcode",
                    "md5",
                }:
                    target = work / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read(name))

    cfg = work / "Metadata" / "model_settings.config"
    if cfg.exists():
        text = cfg.read_text(encoding="utf-8")
        # Drop absolute temp gcode paths; keep relative if we copied plate_N.gcode
        def fix_gcode(m: re.Match[str]) -> str:
            val = m.group(1)
            if val.startswith("/") or ":\\" in val or val.startswith("\\\\"):
                rel = "Metadata/plate_4.gcode"
                # try to detect plate id from path
                mid = re.search(r"plate_(\d+)\.gcode", val)
                if mid:
                    rel = f"Metadata/plate_{mid.group(1)}.gcode"
                if (work / rel).exists():
                    return f'<metadata key="gcode_file" value="{rel}"/>'
                return '<metadata key="gcode_file" value=""/>'
            return m.group(0)

        text = re.sub(
            r'<metadata key="gcode_file" value="([^"]*)"/>',
            fix_gcode,
            text,
        )
        cfg.write_text(text, encoding="utf-8")

    ms_rels = work / "Metadata" / "_rels" / "model_settings.config.rels"
    ms_rels.parent.mkdir(parents=True, exist_ok=True)
    ms_rels.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        "</Relationships>\n",
        encoding="utf-8",
    )

    # Sanity: referenced object paths must be XML, not nested zip
    model_xml = (work / "3D" / "3dmodel.model").read_text(encoding="utf-8")
    refs = re.findall(r'p:path="([^"]+)"', model_xml)
    for ref in refs:
        p = work / ref.lstrip("/")
        if not p.exists():
            print(f"WARNING: missing {ref}", file=sys.stderr)
        elif p.read_bytes()[:2] == b"PK":
            print(f"WARNING: still nested zip: {ref}", file=sys.stderr)

    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(work):
            for name in files:
                full = Path(root) / name
                arc = full.relative_to(work).as_posix()
                info = zipfile.ZipInfo(arc)
                info.flag_bits |= 0x800  # UTF-8
                zf.writestr(info, full.read_bytes())

    shutil.rmtree(work)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
