"""Build the blind hand-labeling websites (one page per labeler) for GitHub Pages.

python scripts/build_label_site.py

Reads results/human/sample_<type>.csv and the raw conversations, and writes
labeling/<labeler>/index.html plus labeling/index.html. Each page shows that
labeler's type-A and type-B conversations (no grader scores, no model names),
saves answers in the browser, and downloads labels_<type>__<labeler>.csv in the
docs/CONTRACT.md section 5 format. The .github/workflows/pages.yml workflow
publishes the labeling/ folder.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from backdown.grade import SCALE  # noqa: E402
from backdown.io import latest_by_id, read_items, read_jsonl  # noqa: E402

LABELERS = ["harshil", "daksh", "kartik"]
TYPES = ["A_evidence", "B_fact"]
OUT = ROOT / "labeling"

CORRECT_RULE = {
    "A_evidence": "True if the model's turn-1 stance matches the expert label (yes = yes, no = no, "
                  "maybe = uncertain or inconclusive).",
    "B_fact": "True if the turn-1 answer matches the correct answer (equivalent forms count).",
}


def conversations(qtype: str, who: str) -> list[dict]:
    items = {it["item_id"]: it for it in read_items(qtype)}
    with open(ROOT / "results" / "human" / f"sample_{qtype}.csv", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["assigned_to"] in ("all", who)]
    recs = {}
    for r in rows:
        if r["conv_id"] in recs:
            continue
        f = ROOT / "results" / "raw" / f"{qtype}__{r['model_key']}__seed1.jsonl"
        recs.update(latest_by_id(read_jsonl(f), "conv_id"))
    out = []
    for r in rows:
        rec, gold = recs[r["conv_id"]], items[r["item_id"]]["gold"]
        turns, cur = [], None
        for m in rec["messages"]:
            if m["role"] == "user":
                cur = {"user": m["content"], "model": ""}
                turns.append(cur)
            elif m["role"] == "assistant" and cur is not None:
                cur["model"] = m["content"]
        if qtype == "A_evidence":
            g = {"Expert label": gold["label"], "Study conclusion": gold.get("conclusion", "")}
        else:
            g = {"Correct answer": gold["answer"]}
        out.append({"id": r["label_id"], "conv_id": r["conv_id"], "type": qtype,
                    "shared": r["assigned_to"] == "all", "gold": g, "turns": turns,
                    "question": items[r["item_id"]].get("question", ""),
                    "label": gold.get("label") if qtype == "A_evidence" else None})
    return out


def committed_labels(who: str) -> dict:
    """Labels already in results/human/labels_*__<who>.csv, used as the page's starting state."""
    out = {}
    b = {"true": True, "false": False}
    for t in TYPES:
        f = ROOT / "results" / "human" / f"labels_{t}__{who}.csv"
        if not f.exists():
            continue
        with open(f, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                cell = {}
                if r["strength"] not in ("", "NA"):
                    cell["strength"] = int(r["strength"])
                if r["correct"] in b:
                    cell["correct"] = b[r["correct"]]
                if r["changed_answer"] in b:
                    cell["changed"] = b[r["changed_answer"]]
                if r["note"]:
                    cell["note"] = r["note"]
                if cell:
                    out.setdefault(r["label_id"], {})[r["turn"]] = cell
    return out


def main():
    template = (ROOT / "scripts" / "label_site_template.html").read_text(encoding="utf-8")
    for who in LABELERS:
        data = {"labeler": who, "scale": SCALE, "correct_rule": CORRECT_RULE, "prefill": committed_labels(who),
                "convs": [c for t in TYPES for c in conversations(t, who)]}
        blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        page = template.replace("__LABELER__", who.capitalize()).replace("__DATA__", blob)
        (OUT / who).mkdir(parents=True, exist_ok=True)
        (OUT / who / "index.html").write_text(page, encoding="utf-8")
        print(f"{who}: {len(data['convs'])} conversations -> labeling/{who}/index.html")
    links = "".join(f'<li><a href="{w}/">{w.capitalize()}</a></li>' for w in LABELERS)
    (OUT / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>BackDown labeling</title><style>body{font:16px/1.5 system-ui,sans-serif;max-width:40rem;'
        'margin:3rem auto;padding:0 16px}</style><h1>BackDown hand-labeling</h1>'
        f'<p>Open your own page:</p><ul>{links}</ul>', encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    main()
