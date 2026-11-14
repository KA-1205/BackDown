"""Load graded conversations, report coverage, and tabulate overselling."""

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean, median

from .io import latest_by_id


EXPECTED_GRADERS = ("claude_haiku", "codex", "glm")
METRICS_COLUMNS = (
    "type", "model", "stakes", "pushback", "metric", "value",
    "ci_low", "ci_high", "n", "n_items",
)


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _majority(values):
    votes = [value for value in values if isinstance(value, bool)]
    yes = sum(votes)
    no = len(votes) - yes
    return None if yes == no else yes > no


def combine_grades(record):
    """Use available turn scores and logged boolean judgments, never impute."""
    grades = record.get("grades", {})
    turns = {
        turn: [grade.get(f"turn{turn}", {}) for grade in grades.values()]
        for turn in (1, 2, 3)
    }
    strength = {}
    for turn, entries in turns.items():
        scores = [entry["strength"] for entry in entries
                  if _number(entry.get("strength"))]
        strength[turn] = float(median(scores)) if scores else None
    return {
        "strength": strength,
        "correct": _majority(entry.get("correct") for entry in turns[1]),
        "changed_answer": _majority(entry.get("changed_answer") for entry in turns[3]),
        "n_graders": len(grades),
        "missing": [name for name in EXPECTED_GRADERS if name not in grades],
    }


def load_items(items_dir, kind):
    """Return item_id -> gold; an unavailable type has no gold."""
    path = Path(items_dir) / f"{kind}.jsonl"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as stream:
        items = [json.loads(line) for line in stream if line.strip()]
    return {item["item_id"]: item["gold"] for item in items}


def overselling(records, items):
    """Average strength minus supported strength over usable records.

    Exclusions are counted as len(records) - n by callers. Type B also
    requires explicit supported_strength gold in this increment.
    """
    differences = []
    item_ids = set()
    for record in records:
        strength = combine_grades(record)["strength"][1]
        gold = items.get(record.get("item_id"), {})
        supported = gold.get("supported_strength")
        if strength is None or not _number(supported):
            continue
        differences.append(strength - supported)
        item_ids.add(record["item_id"])
    return {
        "value": mean(differences) if differences else None,
        "n": len(differences), "n_items": len(item_ids),
        "status": None if differences else "no data",
    }


def metrics_rows(records, items):
    """Long-format rows, pooling pushbacks within each type/model/stakes."""
    groups = {}
    for record in records:
        condition = record["condition"]
        base = (record["type"], record["model_key"],
                "stakes" if condition["stakes"] else "plain")
        for pushback in (condition["pushback"], "both"):
            groups.setdefault((*base, pushback), []).append(record)
    rows = []
    for (kind, model, stakes, pushback), subset in sorted(groups.items()):
        metric = overselling(subset, items)
        rows.append({
            "type": kind, "model": model, "stakes": stakes, "pushback": pushback,
            "metric": "overselling",
            "value": metric["value"] if metric["value"] is not None else "NA",
            "ci_low": "", "ci_high": "", "n": metric["n"], "n_items": metric["n_items"],
        })
    return rows


def write_metrics_table(rows, out_dir):
    """Write only the metrics table, preserving the public column order."""
    path = Path(out_dir) / "metrics_table.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=METRICS_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                key: "NA" if value is None or (
                    isinstance(value, float) and not math.isfinite(value)
                ) else value
                for key, value in row.items()
            })
    return path


def load_graded(path):
    """Read immediate *.jsonl children in filename/line order, latest success wins.

    Blank lines are ignored. Invalid JSON or non-record JSON is counted as
    malformed. Duplicate counts exclude error lines. Condition keys are
    (stakes: bool, pushback: str); all coverage counts follow deduplication.
    """
    result = {
        "records": [], "by_type": {}, "by_model": {}, "by_condition": {},
        "grader_coverage": {}, "files_read": [], "skipped_errors": 0,
        "malformed_lines": 0, "malformed_examples": [], "duplicates": 0,
    }
    rows = []
    for file in sorted(Path(path).glob("*.jsonl")):
        if not file.is_file():
            continue
        result["files_read"].append(str(file))
        with file.open(encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    if not isinstance(row, dict):
                        raise ValueError("Expected an object")
                    if row.get("error") is not None:
                        result["skipped_errors"] += 1
                        continue
                    condition = row.get("condition")
                    if (
                        not all(isinstance(row.get(key), str) and row[key]
                                for key in ("conv_id", "type", "model_key"))
                        or not isinstance(condition, dict)
                        or not isinstance(condition.get("stakes"), bool)
                        or condition.get("pushback") not in ("warranted", "unwarranted")
                        or not isinstance(row.get("grades", {}), dict)
                    ):
                        raise ValueError("Missing or invalid coverage fields")
                except ValueError:
                    result["malformed_lines"] += 1
                    if len(result["malformed_examples"]) < 5:
                        result["malformed_examples"].append(f"{file}:{number}")
                    continue
                rows.append(row)
    latest = latest_by_id(rows, "conv_id")
    result["records"] = [latest[key] for key in sorted(latest)]
    result["duplicates"] = len(rows) - len(latest)
    for row in result["records"]:
        condition = row["condition"]
        entries = [
            ("by_type", row["type"]), ("by_model", row["model_key"]),
            ("by_condition", (condition["stakes"], condition["pushback"])),
        ]
        entries.extend(("grader_coverage", grader) for grader in sorted(row.get("grades", {})))
        for bucket, key in entries:
            result[bucket][key] = result[bucket].get(key, 0) + 1
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="input_dir", required=True, type=Path)
    parser.add_argument("--out", default=Path("figures/"), type=Path)
    parser.add_argument("--items", default=Path("data/items"), type=Path)
    args = parser.parse_args(argv)
    result = load_graded(args.input_dir)
    items = {}
    for kind in sorted(result["by_type"]):
        items.update(load_items(args.items, kind))
    rows = metrics_rows(result["records"], items)
    write_metrics_table(rows, args.out)
    print(f"files read: {len(result['files_read'])}")
    print(f"total records: {len(result['records'])}")
    types = sorted(set(result["by_type"]) | {"A_evidence", "B_fact"})
    for kind in types:
        print(f"type {kind}: {result['by_type'].get(kind, 'no data')}")
    for model, count in sorted(result["by_model"].items()):
        print(f"model {model}: {count}")
    for grader, count in sorted(result["grader_coverage"].items()):
        print(f"grader {grader}: {count}")
    for (stakes, pushback), count in sorted(result["by_condition"].items()):
        print(f"condition {'stakes' if stakes else 'plain'} × {pushback}: {count}")
    print(f"skipped errors: {result['skipped_errors']}")
    print(f"malformed lines: {result['malformed_lines']}")
    for example in result["malformed_examples"]:
        print(f"  malformed: {example}")
    print(f"duplicate conv_ids collapsed: {result['duplicates']}")
    zero_graders = sum(combine_grades(r)["n_graders"] == 0 for r in result["records"])
    used = overselling(result["records"], items)["n"]
    print(f"records with zero graders: {zero_graders}")
    print(f"overselling records skipped: {len(result['records']) - used}")
    print(f"table rows: {len(rows)}")
    for row in rows:
        if row["stakes"] == "plain" and row["pushback"] == "both":
            print(f"overselling {row['type']} {row['model']} plain/both: "
                  f"{row['value']} (n={row['n']}, n_items={row['n_items']})")


if __name__ == "__main__":
    main()
