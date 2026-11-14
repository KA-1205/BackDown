"""Load graded conversations and report coverage; no metrics yet."""

import argparse
import json
from pathlib import Path

from .io import latest_by_id


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
    args = parser.parse_args(argv)
    result = load_graded(args.input_dir)
    args.out.mkdir(parents=True, exist_ok=True)
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


if __name__ == "__main__":
    main()
