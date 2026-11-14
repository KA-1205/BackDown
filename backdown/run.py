"""Collect 3-turn BackDown conversations.

python -m backdown.run --type A_evidence --models gpt41,gemini_flash --seed 1 --limit 3
"""

import argparse
import asyncio
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .clients import chat
from .config import ROOT, harness_version, load_config, resolve
from .io import append_jsonl, read_items, read_jsonl

SYSTEM_PROMPT = "You are a helpful assistant."
TEMPLATE_KEYS = ["turn1", "stakes", "probe", "pushback_warranted", "pushback_unwarranted", "explicit_confidence"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def pick_templates(templates: dict, seed: int, item_id: str, stakes: bool, pushback: str) -> dict[str, int]:
    """Same wording for every model, so models are compared on identical prompts.
    A different seed gives a different wording (rotation)."""
    h = hashlib.sha256(f"{seed}|{item_id}|{stakes}|{pushback}".encode()).hexdigest()
    rng = random.Random(int(h[:16], 16))
    return {k: rng.randrange(len(templates[k])) for k in TEMPLATE_KEYS if templates.get(k)}


def build_turns(item: dict, templates: dict, choice: dict, stakes: bool, pushback: str, variant: str) -> list[str]:
    fmt = {"question": item["question"], "context": item.get("context") or "", "claim_hint": item["claim_hint"],
           "evidence": item["warranted_evidence"]}
    t1 = templates["turn1"][choice["turn1"]].format(**fmt).strip()
    if stakes:
        t1 += "\n\n" + templates["stakes"][choice["stakes"]]
    if variant == "explicit_confidence":
        t1 += "\n\n" + templates["explicit_confidence"][choice["explicit_confidence"]]
    t2 = templates["probe"][choice["probe"]].format(**fmt)
    key = "pushback_warranted" if pushback == "warranted" else "pushback_unwarranted"
    t3 = templates[key][choice[key]].format(**fmt)
    return [t1, t2, t3]


def out_path(qtype: str, model_key: str, seed: int, variant: str) -> Path:
    suffix = "" if variant == "natural" else f"__{variant}"
    return ROOT / "results" / "raw" / f"{qtype}__{model_key}__seed{seed}{suffix}.jsonl"


async def run_one(route, item, templates, stakes, pushback, variant, seed, params, client, path, hv):
    choice = pick_templates(templates, seed, item["item_id"], stakes, pushback)
    conv_id = f"{item['item_id']}__{route.model_key}__{'stakes' if stakes else 'plain'}__{pushback}__{variant}__seed{seed}"
    turns = build_turns(item, templates, choice, stakes, pushback, variant)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    rec = {"conv_id": conv_id, "item_id": item["item_id"], "type": item["type"], "model_key": route.model_key,
           "provider": route.provider, "model_requested": route.model, "model_returned": None,
           "condition": {"stakes": stakes, "pushback": pushback, "variant": variant},
           "seed": seed, "template_choice": choice, "messages": messages, "turn_meta": [],
           "started_at": now(), "finished_at": None, "error": None, "harness_version": hv}
    try:
        for user_msg in turns:
            messages.append({"role": "user", "content": user_msg})
            reply = await chat(route, messages, client=client, **params)
            messages.append({"role": "assistant", "content": reply.text})
            rec["model_returned"] = reply.model_returned
            rec["turn_meta"].append({"latency_s": reply.latency_s, "usage": reply.usage,
                                     "finish_reason": reply.finish_reason, "attempts": reply.attempts})
    except Exception as e:  # keep partial conversation for debugging; analysis skips it
        rec["error"] = str(e)[:1000]
    rec["finished_at"] = now()
    append_jsonl(path, rec)
    return rec


async def main_async(args):
    cfg = load_config()
    items = read_items(args.type)
    if args.limit:
        items = items[: args.limit]
    templates = json.loads((ROOT / "templates" / f"{args.type}.json").read_text(encoding="utf-8"))
    params = cfg["subject_params"]
    hv = harness_version()
    stakes_levels = [False] if args.no_stakes else [False, True]
    pushbacks = [p for p in ["warranted", "unwarranted"] if args.pushback in ("both", p)]

    jobs = []
    for mk in args.models.split(","):
        route = resolve(mk.strip(), "subjects", args.route)
        path = out_path(args.type, route.model_key, args.seed, args.variant)
        done = {r["conv_id"] for r in read_jsonl(path) if r.get("error") is None}
        n_new = 0
        for item in items:
            for stakes in stakes_levels:
                for pb in pushbacks:
                    cid = f"{item['item_id']}__{route.model_key}__{'stakes' if stakes else 'plain'}__{pb}__{args.variant}__seed{args.seed}"
                    if cid in done:
                        continue
                    jobs.append((route, item, stakes, pb, path))
                    n_new += 1
        print(f"{mk}: route={route.provider}/{route.model} todo={n_new} done={len(done)} -> {path.relative_to(ROOT)}")

    if args.dry_run or not jobs:
        return
    ok = err = 0
    # Limit conversations in flight per model, so each one finishes (and is saved) before new ones start.
    conv_sems = {}

    async def bounded(r, it, s, pb, p):
        sem = conv_sems.setdefault(r.model_key, asyncio.Semaphore(r.concurrency))
        async with sem:
            return await run_one(r, it, templates, s, pb, args.variant, args.seed, params, client, p, hv)

    async with httpx.AsyncClient() as client:
        tasks = [bounded(r, it, s, pb, p) for r, it, s, pb, p in jobs]
        for fut in asyncio.as_completed(tasks):
            rec = await fut
            if rec["error"]:
                err += 1
                print(f"  ERR {rec['conv_id']}: {rec['error'][:160]}", file=sys.stderr)
            else:
                ok += 1
            if (ok + err) % 10 == 0 or ok + err == len(tasks):
                print(f"  progress {ok + err}/{len(tasks)} ok={ok} err={err}", flush=True)
    print(f"Finished: ok={ok} err={err}. Re-run the same command to retry failed conversations.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--type", required=True, help="A_evidence or B_fact")
    ap.add_argument("--models", required=True, help="comma-separated subject keys from config/models.json")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0, help="only the first N items")
    ap.add_argument("--variant", default="natural", choices=["natural", "explicit_confidence"])
    ap.add_argument("--no-stakes", action="store_true", help="plain condition only")
    ap.add_argument("--pushback", default="both", choices=["both", "warranted", "unwarranted"])
    ap.add_argument("--route", default=None, help="force a provider, e.g. freellmapi")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
