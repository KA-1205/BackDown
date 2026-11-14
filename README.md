# BackDown

BackDown measures the gap between what a language model **says** in its first answer and what it **stands by** when challenged. It separates justified updating (warranted pushback with real evidence) from caving (unwarranted pushback).

Built during the Apart Research AI x Epistemics Research Sprint, 13 to 15 Nov 2026. All code in this repository was written during the sprint.

## Start here

- `docs/SPEC.md`: the full plan
- `docs/CONTRACT.md`: shared file formats
- `DAKSH.md`, `KARTIK.md`: per-person briefs

## Quick start

```bash
pip install -r requirements.txt
python scripts/build_pubmedqa.py
python -m backdown.run --type A_evidence --models gpt41 --seed 1 --limit 1
python -m backdown.grade --type A_evidence
```

API keys come from environment variables only. See `config/models.json` for the names.
