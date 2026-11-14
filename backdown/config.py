import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "models.json"

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass


@dataclass(frozen=True)
class Route:
    model_key: str
    provider: str
    kind: str
    model: str
    base_url: str | None
    key_env: str | None
    concurrency: int

    @property
    def api_key(self) -> str | None:
        return os.environ.get(self.key_env) if self.key_env else None


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _available(provider_cfg: dict) -> bool:
    key_env = provider_cfg.get("key_env")
    return key_env is None or bool(os.environ.get(key_env))


def resolve(model_key: str, section: str, force_provider: str | None = None) -> Route:
    cfg = load_config()
    routes = cfg[section].get(model_key)
    if routes is None:
        raise SystemExit(f"Unknown {section[:-1]} '{model_key}'. Known: {', '.join(cfg[section])}")
    for r in routes:
        if force_provider and r["provider"] != force_provider:
            continue
        p = cfg["providers"][r["provider"]]
        if force_provider or _available(p):
            return Route(
                model_key=model_key,
                provider=r["provider"],
                kind=p["kind"],
                model=r["model"],
                base_url=p.get("base_url"),
                key_env=p.get("key_env"),
                concurrency=p.get("concurrency", 2),
            )
    raise SystemExit(f"No usable route for '{model_key}': set one of the key variables for {[r['provider'] for r in routes]}")


def harness_version() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=10)
        dirty = subprocess.run(["git", "status", "--porcelain", "backdown", "templates", "config"], cwd=ROOT, capture_output=True, text=True, timeout=10)
        return out.stdout.strip() + ("-dirty" if dirty.stdout.strip() else "")
    except Exception:
        return "unknown"
