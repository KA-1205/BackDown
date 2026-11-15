"""Copy grades from committed results/graded files into the local grade cache.

python scripts/seed_cache_from_graded.py --type B_fact

backdown.grade rebuilds results/graded only from results/graded/_cache (git-ignored).
Grades made on another machine are only in the graded files, so a merge here would
drop them. This script adds them to the cache (only conversations the cache does not
already have), so merges keep them and graders skip them.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backdown.grade import cache_path  # noqa: E402
from backdown.io import append_jsonl, read_jsonl  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", required=True)
    args = ap.parse_args()
    for gf in sorted((ROOT / "results" / "graded").glob(f"{args.type}__*.jsonl")):
        raw = ROOT / "results" / "raw" / gf.name
        if not raw.exists():
            print(f"skip {gf.name}: no raw file")
            continue
        added = {}
        for rec in read_jsonl(gf):
            for grader, g in rec.get("grades", {}).items():
                cp = cache_path(raw, grader)
                done = {r["conv_id"] for r in read_jsonl(cp) if r.get("grade")}
                if rec["conv_id"] in done:
                    continue
                grade = {k: v for k, v in g.items() if k != "route"}
                append_jsonl(cp, {"conv_id": rec["conv_id"], "grader": grader, "grader_route": g.get("route"),
                                  "grade": grade, "error": None})
                added[grader] = added.get(grader, 0) + 1
        print(f"{gf.name}: added {added or 'nothing'}")


if __name__ == "__main__":
    main()
