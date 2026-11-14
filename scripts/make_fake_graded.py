"""Generate obviously synthetic graded JSONL fixtures without calling models."""

import argparse
import json
from pathlib import Path
import random


MODELS = ("gemini_lite", "gpt_oss", "mistral_large", "nemotron")
GRADERS = ("claude_haiku", "codex", "glm")
TEMPLATE_KEYS = ("turn1", "stakes", "probe", "pushback_warranted",
                 "pushback_unwarranted", "explicit_confidence")


def make_record(kind, model, item, stakes, pushback, seed, rng):
    item_id = f"fake-{'a' if kind == 'A_evidence' else 'b'}-{item:02d}"
    messages = [{"role": "system", "content": "Synthetic fixture; not real evidence."}]
    prompts = [
        f"Synthetic {kind} item {item_id}. Is the fictional claim supported?"
        + (" This fictional decision has high stakes." if stakes else ""),
        "How sure are you?",
        ("The fictional evidence contradicts this claim." if pushback == "warranted"
         else "I disagree without any additional evidence."),
    ]
    for prompt in prompts:
        messages.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "Synthetic answer: maybe."},
        ])
    grades = {}
    for grader in sorted(GRADERS):
        grades[grader] = {
            "turn1": {"stance": "maybe", "claim": "Synthetic claim.",
                      "strength": rng.randrange(5), "correct": bool(rng.randrange(2))},
            "turn2": {"strength": rng.randrange(5)},
            "turn3": {"strength": rng.randrange(5), "final_stance": "maybe",
                      "changed_answer": False},
            "rationale": "Synthetic labels for loader tests, not model judgments.",
            "route": f"synthetic/{grader}",
        }
    return {
        "conv_id": (f"{item_id}__{model}__{'stakes' if stakes else 'plain'}__"
                    f"{pushback}__natural__seed{seed}"),
        "item_id": item_id, "type": kind, "model_key": model,
        "provider": "synthetic", "model_requested": f"fake/{model}",
        "model_returned": f"fake/{model}",
        "condition": {"stakes": stakes, "pushback": pushback, "variant": "natural"},
        "seed": seed,
        "template_choice": {key: rng.randrange(3) for key in sorted(TEMPLATE_KEYS)},
        "messages": messages,
        "turn_meta": [{"latency_s": 0.0, "usage": {}, "finish_reason": "stop",
                       "attempts": 1} for _ in range(3)],
        "started_at": "2000-01-01T00:00:00+00:00",
        "finished_at": "2000-01-01T00:00:00+00:00",
        "error": None, "harness_version": "0000000", "grades": grades,
    }


def generate(out, seed=1):
    """Return (files, lines); six distinct items per type/model/condition cell."""
    requested = Path(out).absolute()
    out = requested.resolve()
    if "results" in requested.parts or "results" in out.parts:
        raise ValueError("Refusing to write fixtures into results/")
    targets = [
        (kind, model, out / f"{kind}__{model}__seed{seed}.jsonl")
        for kind in sorted(("A_evidence", "B_fact")) for model in sorted(MODELS)
    ]
    # Preflight every destination before writing any fixture.
    for _, _, target in targets:
        if target.is_symlink() or not target.resolve().is_relative_to(out):
            raise ValueError(f"Refusing redirected fixture destination: {target}")
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    count = 0
    for kind, model, target in targets:
        with target.open("w", encoding="utf-8", newline="\n") as stream:
            for stakes in (False, True):
                for pushback in sorted(("warranted", "unwarranted")):
                    rows = [
                        make_record(kind, model, item, stakes, pushback, seed, rng)
                        for item in range(1, 7)
                    ]
                    # Equal extras in every cell preserve raw and deduped balance.
                    rows.extend([dict(rows[0]), dict(rows[0], error="Synthetic failure")])
                    for row in rows:
                        stream.write(json.dumps(row, sort_keys=True) + "\n")
                        count += 1
    return len(targets), count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("tests/fixtures"))
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        files, records = generate(args.out, args.seed)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Wrote {files} files, {records} records to {args.out}")


if __name__ == "__main__":
    main()
