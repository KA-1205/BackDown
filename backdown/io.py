import json
import threading
from pathlib import Path

from .config import ROOT

_lock = threading.Lock()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock, path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_items(qtype: str) -> list[dict]:
    path = ROOT / "data" / "items" / f"{qtype}.jsonl"
    if not path.exists():
        raise SystemExit(f"Missing {path}. Build the items first.")
    return read_jsonl(path)


def latest_by_id(rows: list[dict], key: str) -> dict[str, dict]:
    """Later lines win, so a successful retry replaces an earlier failed attempt."""
    out = {}
    for r in rows:
        if r.get("error") is None or r[key] not in out:
            out[r[key]] = r
    return out
