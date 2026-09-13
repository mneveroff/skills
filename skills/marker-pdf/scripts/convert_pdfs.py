#!/usr/bin/env python3
"""Convert PDFs with marker-pdf. Writes <parent>/<stem>/ beside each PDF."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def default_gemini_model(python_bin: Path) -> str:
    code = (
        "from marker.services.gemini import BaseGeminiService; "
        "print(BaseGeminiService.model_fields['gemini_model_name'].default)"
    )
    result = subprocess.run(
        [str(python_bin), "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )
    model = result.stdout.strip()
    if not model:
        raise RuntimeError("Could not read Marker Gemini default model.")
    return model


def collect_pdfs(inputs: list[Path]) -> list[Path]:
    pdfs: list[Path] = []
    for item in inputs:
        if item.is_dir():
            pdfs.extend(sorted(p for p in item.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"))
        elif item.is_file() and item.suffix.lower() == ".pdf":
            pdfs.append(item)
        else:
            print(f"skip (not a pdf): {item}", file=sys.stderr)
    return pdfs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert PDFs with marker-pdf into sibling folders named after each PDF."
    )
    parser.add_argument("paths", nargs="+", type=Path, help="PDF files or folders of PDFs")
    parser.add_argument(
        "--venv",
        type=Path,
        default=Path(".venv"),
        help="Project virtualenv (default: .venv)",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(".env"),
        help="Env file with GEMINI_API_KEY (default: .env)",
    )
    args = parser.parse_args()

    load_dotenv(args.env_file)
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print("GEMINI_API_KEY is missing from .env", file=sys.stderr)
        return 1
    os.environ["GOOGLE_API_KEY"] = key

    python_bin = args.venv / "bin" / "python"
    marker_single = args.venv / "bin" / "marker_single"
    if not marker_single.is_file():
        print(f"marker_single not found at {marker_single}", file=sys.stderr)
        return 1

    pdfs = collect_pdfs([p.resolve() for p in args.paths])
    if not pdfs:
        print("No PDFs found.", file=sys.stderr)
        return 1

    model = default_gemini_model(python_bin)
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    for pdf in pdfs:
        output_dir = pdf.parent
        cmd = [
            str(marker_single),
            str(pdf),
            "--output_dir",
            str(output_dir),
            "--use_llm",
            "--gemini_model_name",
            model,
            "--workers",
            "1",
        ]
        print(f"converting {pdf.name} -> {output_dir / pdf.stem}/")
        subprocess.run(cmd, check=True, env=env)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
