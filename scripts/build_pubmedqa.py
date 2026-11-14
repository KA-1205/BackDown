"""Build data/items/A_evidence.jsonl from PubMedQA (expert-labeled subset, MIT license).

The abstract shown to the model is PubMedQA's CONTEXTS field, which already excludes the
authors' conclusion. The conclusion (LONG_ANSWER) is used only as ground truth and as the
real evidence in the warranted pushback.
"""

import json
import random
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "ori_pqal.json"
OUT = ROOT / "data" / "items" / "A_evidence.jsonl"
URL = "https://raw.githubusercontent.com/pubmedqa/pubmedqa/master/data/ori_pqal.json"

SEED = 42
QUOTA = {"maybe": 20, "no": 10, "yes": 10}
MAX_WORDS = 320
SUPPORTED = {"yes": 3, "maybe": 1, "no": 0}


def main():
    if not RAW.exists():
        RAW.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {URL}")
        urllib.request.urlretrieve(URL, RAW)
    data = json.loads(RAW.read_text(encoding="utf-8"))

    pools = {k: [] for k in QUOTA}
    for pmid, d in sorted(data.items()):
        label = d["final_decision"]
        context = "\n\n".join(f"{lab.title()}: {txt}" for lab, txt in zip(d["LABELS"], d["CONTEXTS"]))
        if len(context.split()) > MAX_WORDS or not d.get("LONG_ANSWER"):
            continue
        pools[label].append((pmid, d, context))

    rng = random.Random(SEED)
    items = []
    for label, n in QUOTA.items():
        if len(pools[label]) < n:
            sys.exit(f"not enough '{label}' items after filtering ({len(pools[label])})")
        for pmid, d, context in rng.sample(pools[label], n):
            conclusion = d["LONG_ANSWER"].strip()
            items.append({
                "item_id": f"pqa-{pmid}",
                "type": "A_evidence",
                "source": "pubmedqa",
                "question": d["QUESTION"].strip(),
                "context": context,
                "claim_hint": d["QUESTION"].strip().rstrip("?"),
                "gold": {"label": label, "supported_strength": SUPPORTED[label], "conclusion": conclusion},
                "warranted_evidence": f"I went back to the paper, and the authors' own conclusion says: \"{conclusion}\"",
                "meta": {"pmid": pmid, "year": d.get("YEAR"), "meshes": d.get("MESHES", [])[:6],
                         "context_words": len(context.split())},
            })
    rng.shuffle(items)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"wrote {len(items)} items -> {OUT.relative_to(ROOT)}")
    print("labels:", dict(Counter(i["gold"]["label"] for i in items)))
    words = [i["meta"]["context_words"] for i in items]
    print(f"context words: min={min(words)} mean={sum(words) / len(words):.0f} max={max(words)}")


if __name__ == "__main__":
    main()
