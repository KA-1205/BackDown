"""Show collection and grading progress for every raw results file.

python scripts/status.py
"""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backdown.io import latest_by_id, read_jsonl  # noqa: E402


def main():
    raw_dir = ROOT / "results" / "raw"
    cache_dir = ROOT / "results" / "graded" / "_cache"
    print(f"{'raw file':55s} {'ok':>4s} {'err':>4s} {'trunc':>5s}  graded per grader")
    for rf in sorted(raw_dir.glob("*.jsonl")):
        recs = latest_by_id(read_jsonl(rf), "conv_id")
        c = Counter("err" if r.get("error") else "ok" for r in recs.values())
        trunc = sum(1 for r in recs.values() if any(t.get("finish_reason") == "length" for t in r.get("turn_meta", [])))
        graded = []
        for cf in sorted(cache_dir.glob(f"{rf.stem}__*.jsonl")):
            g = cf.stem[len(rf.stem) + 2:]
            if "__" in g:
                continue
            n = sum(1 for r in latest_by_id(read_jsonl(cf), "conv_id").values() if r.get("grade"))
            graded.append(f"{g}={n}")
        print(f"{rf.name:55s} {c['ok']:4d} {c['err']:4d} {trunc:5d}  {' '.join(graded)}")


if __name__ == "__main__":
    main()
