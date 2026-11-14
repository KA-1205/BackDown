"""Model clients. OpenAI-compatible HTTP endpoints for models under test and graders.
CLI tools (claude -p, opencode run, codex exec) are allowed only as graders."""

import asyncio
import json
import random
import re
import shutil
import tempfile
import time
from dataclasses import dataclass, field

import httpx

from .config import Route, load_config

RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 529}
_semaphores: dict[str, asyncio.Semaphore] = {}


@dataclass
class Reply:
    text: str
    model_returned: str | None
    latency_s: float
    usage: dict | None = None
    finish_reason: str | None = None
    attempts: int = 1
    extra: dict = field(default_factory=dict)


def _sem(route: Route) -> asyncio.Semaphore:
    if route.provider not in _semaphores:
        _semaphores[route.provider] = asyncio.Semaphore(route.concurrency)
    return _semaphores[route.provider]


async def chat(route: Route, messages: list[dict], *, temperature: float, max_tokens: int,
               client: httpx.AsyncClient, max_attempts: int = 8) -> Reply:
    async with _sem(route):
        if route.kind == "openai":
            return await _chat_openai(route, messages, temperature, max_tokens, client, max_attempts)
        if route.kind == "cli":
            return await _chat_cli(route, messages, max_attempts)
        raise ValueError(f"Unknown provider kind {route.kind}")


async def _chat_openai(route, messages, temperature, max_tokens, client, max_attempts) -> Reply:
    url = route.base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {route.api_key}", "Content-Type": "application/json"}
    body = {"model": route.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    last_err = None
    for attempt in range(1, max_attempts + 1):
        t0 = time.perf_counter()
        try:
            r = await client.post(url, headers=headers, json=body, timeout=180)
            if r.status_code in RETRY_STATUS:
                last_err = f"HTTP {r.status_code}: {r.text[:300]}"
                retry_after = r.headers.get("retry-after")
                wait = float(retry_after) if retry_after and retry_after.replace(".", "").isdigit() else min(90, 2 ** attempt)
                await asyncio.sleep(wait + random.random())
                continue
            if r.status_code >= 400:
                raise RuntimeError(f"HTTP {r.status_code}: {r.text[:500]}")
            data = r.json()
            choice = data["choices"][0]
            text = choice["message"].get("content") or ""
            if not text.strip():
                last_err = "empty response"
                await asyncio.sleep(2 ** attempt)
                continue
            return Reply(text=text, model_returned=data.get("model"), latency_s=round(time.perf_counter() - t0, 2),
                         usage=data.get("usage"), finish_reason=choice.get("finish_reason"), attempts=attempt)
        except (httpx.TransportError, httpx.TimeoutException, json.JSONDecodeError, KeyError) as e:
            last_err = f"{type(e).__name__}: {e}"
            await asyncio.sleep(min(60, 2 ** attempt))
    raise RuntimeError(f"{route.provider}/{route.model} failed after {max_attempts} attempts: {last_err}")


def _flatten(messages: list[dict]) -> tuple[str, str]:
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    rest = [m for m in messages if m["role"] != "system"]
    if len(rest) == 1 and rest[0]["role"] == "user":
        return system, rest[0]["content"]
    return system, "\n\n".join(f"[{m['role'].upper()}]\n{m['content']}" for m in rest)


_SANDBOX = tempfile.mkdtemp(prefix="backdown_cli_")
_ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def _clean_cli(raw: str) -> str:
    lines = [_ANSI.sub("", ln) for ln in raw.splitlines()]
    lines = [ln for ln in lines if not ln.strip().startswith("> ")]  # opencode "> build · model" header
    return "\n".join(lines).strip()


async def _chat_cli(route: Route, messages, max_attempts) -> Reply:
    p = load_config()["providers"][route.provider]
    system, prompt = _flatten(messages)
    subs = {"model": route.model, "system": system or "You are a careful grader.", "prompt": prompt}
    cmd = [part.format(**subs) if "{" in part else part for part in p["cmd"]]
    exe = shutil.which(cmd[0])
    if exe is None:
        raise RuntimeError(f"CLI '{cmd[0]}' not found on PATH")
    cmd[0] = exe
    stdin_data = prompt.encode("utf-8") if p.get("prompt_via") == "stdin" else None
    last_err = None
    for attempt in range(1, min(max_attempts, 4) + 1):
        t0 = time.perf_counter()
        # Run in an empty temp folder so an agent CLI cannot see or touch the repo.
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdin=asyncio.subprocess.PIPE if stdin_data else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=_SANDBOX)
        try:
            out, err = await asyncio.wait_for(proc.communicate(stdin_data), timeout=300)
        except asyncio.TimeoutError:
            proc.kill()
            last_err = "timeout"
            continue
        text = _clean_cli(out.decode("utf-8", errors="replace"))
        if proc.returncode == 0 and text:
            return Reply(text=text, model_returned=f"{route.provider}:{route.model}",
                         latency_s=round(time.perf_counter() - t0, 2), attempts=attempt)
        last_err = f"exit {proc.returncode}: {err.decode('utf-8', errors='replace')[:300]}"
        await asyncio.sleep(5 * attempt)
    raise RuntimeError(f"{route.provider} CLI failed: {last_err}")
