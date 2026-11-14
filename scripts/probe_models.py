"""Send one tiny prompt to each candidate route and report which ones work.

python scripts/probe_models.py groq:llama-3.3-70b-versatile gemini:gemini-3.5-flash
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backdown.config import load_config  # noqa: E402


def main():
    cfg = load_config()["providers"]
    if not os.environ.get("GITHUB_TOKEN"):
        try:
            os.environ["GITHUB_TOKEN"] = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
        except FileNotFoundError:
            pass
    for spec in sys.argv[1:]:
        prov, model = spec.split(":", 1)
        p = cfg[prov]
        key = os.environ.get(p["key_env"] or "", "")
        t0 = time.perf_counter()
        try:
            r = httpx.post(p["base_url"].rstrip("/") + "/chat/completions",
                           headers={"Authorization": f"Bearer {key}"},
                           json={"model": model, "messages": [{"role": "user", "content": "Reply with the word OK."}],
                                 "max_tokens": 20, "temperature": 0}, timeout=60)
            ok = r.status_code == 200
            info = r.json().get("model") if ok else r.text[:150].replace("\n", " ")
        except Exception as e:
            ok, info = False, str(e)[:150]
        print(f"{'OK ' if ok else 'BAD'} {spec:55s} {time.perf_counter() - t0:5.1f}s {info}")


if __name__ == "__main__":
    main()
