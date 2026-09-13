---
name: marker-pdf
description: Convert PDFs to markdown with marker-pdf and a Gemini key from .env. Use when converting PDFs with marker, marker-pdf, Gemini OCR, or extracting markdown from PDF docs.
---

# Marker PDF

Convert PDFs to markdown with `marker-pdf` and Gemini. Read `GEMINI_API_KEY` from `.env`. Never print, log, commit, or put the key on a command line.

## Quick start

From the project root, after the venv exists, run [scripts/convert_pdfs.py](scripts/convert_pdfs.py) from this skill directory:

```bash
.venv/bin/python /path/to/marker-pdf/scripts/convert_pdfs.py path/to/file.pdf
.venv/bin/python /path/to/marker-pdf/scripts/convert_pdfs.py path/to/folder
```

Output is a sibling folder named after the PDF stem:

```
docs/manual.pdf
docs/manual/manual.md
```

Do not write a shared `converted/` parent folder.

## Workflow

1. **Secrets.** Confirm `.env` has `GEMINI_API_KEY`. If missing, stop. Do not ask the user to paste a key into chat. Load via `source .env` or the script. Export `GOOGLE_API_KEY` from that value for Marker. Never `echo`, `cat .env`, or pass `--gemini_api_key`.
2. **Venv.** If `.venv` is missing: `uv venv .venv --python 3.12` then `uv pip install marker-pdf --python .venv/bin/python`. Use Python 3.12 (PyTorch often fails on newer versions).
3. **Model.** Use the installed Marker Gemini default (Flash-tier). Read it with:

   ```bash
   .venv/bin/python -c "from marker.services.gemini import BaseGeminiService; print(BaseGeminiService.model_fields['gemini_model_name'].default)"
   ```

   Pass that as `--gemini_model_name`. If it looks retired, check [datalab-to/marker](https://github.com/datalab-to/marker) README and pick the current affordable Flash default. Do not use Pro models unless the user asks.
4. **Convert.** Call [scripts/convert_pdfs.py](scripts/convert_pdfs.py) on the files or folder. It runs `marker_single` per PDF with `--output_dir` set to the PDF parent, `--use_llm`, `--workers 1`. Skip non-PDFs.
5. **Report.** List output `.md` paths. Note table-OCR warnings. Do not quote env values.

## Rules

- One folder per PDF, same directory as the PDF, folder name = stem (no `.pdf`).
- Do not write a shared `converted/` (or similar) parent folder.
- Do not commit `.env`, keys, or Marker caches.
- Spaces in filenames are normal; quote paths.
