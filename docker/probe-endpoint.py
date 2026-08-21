#!/usr/bin/env python3
"""Probe an OpenAI-compatible endpoint for what this pipeline actually needs.

Reads .env from the repo root. Never prints the API key.

    python3.12 docker/probe-endpoint.py
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env() -> dict:
    env = {}
    path = ROOT / ".env"
    if not path.is_file():
        sys.exit(f"error: {path} not found — create it first")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def post(base_url: str, api_key: str, payload: dict, timeout: int = 120):
    url = base_url.rstrip("/") + "/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
        return e.code, body
    except Exception as e:
        return 0, str(e)


def brief(body, limit=300):
    text = body if isinstance(body, str) else json.dumps(body)
    return text[:limit] + ("..." if len(text) > limit else "")


def main():
    env = load_env()
    base_url = env.get("LLM_BASE_URL", "https://api.openai.com/v1")
    api_key = env.get("LLM_API_KEY", "")
    model = env.get("MODEL", "")

    if not api_key:
        sys.exit("error: LLM_API_KEY is empty in .env")
    if not model:
        sys.exit("error: MODEL is empty in .env")

    print(f"endpoint : {base_url}")
    print(f"model    : {model}")
    print()

    results = {}

    # 1. Does the model answer at all?
    print("[1/4] basic chat completion ...", flush=True)
    status, body = post(base_url, api_key, {
        "model": model,
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
        "temperature": 0.0,
        "max_tokens": 16,
    })
    if status == 200:
        content = body["choices"][0]["message"].get("content")
        print(f"      OK  -> {content!r}")
        results["basic"] = True
    else:
        print(f"      FAIL (HTTP {status}) {brief(body)}")
        results["basic"] = False

    # 2. Tool calling — the pipeline cannot work without it.
    print("[2/4] tool calling (REQUIRED by every agent) ...", flush=True)
    status, body = post(base_url, api_key, {
        "model": model,
        "messages": [{"role": "user", "content": "What is the weather in Hanoi? Use the tool."}],
        "temperature": 0.0,
        "max_tokens": 256,
        "tools": [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        }],
        "tool_choice": "auto",
    })
    if status == 200:
        msg = body["choices"][0]["message"]
        calls = msg.get("tool_calls")
        if calls:
            fn = calls[0].get("function", {})
            print(f"      OK  -> tool_calls: {fn.get('name')}({fn.get('arguments')})")
            results["tools"] = True
        else:
            print(f"      NO TOOL CALL -> replied as plain text: {brief(msg.get('content'), 160)!r}")
            results["tools"] = False
    else:
        print(f"      FAIL (HTTP {status}) {brief(body)}")
        results["tools"] = False

    # 3 & 4. Hardcoded output-token ceilings in llm_services.py.
    for i, limit in ((3, 16000), (4, 32768)):
        print(f"[{i}/4] max_tokens={limit} accepted? ...", flush=True)
        status, body = post(base_url, api_key, {
            "model": model,
            "messages": [{"role": "user", "content": "Say OK"}],
            "temperature": 0.0,
            "max_tokens": limit,
        })
        ok = status == 200
        print("      OK" if ok else f"      REJECTED (HTTP {status}) {brief(body)}")
        results[f"max_tokens_{limit}"] = ok

    print()
    print("=" * 60)
    if not results.get("basic"):
        print("BLOCKED: the endpoint/model/key combination does not answer.")
    elif not results.get("tools"):
        print("BLOCKED: no tool calling. Every agent in this pipeline is built")
        print("with tools=[...] (pydantic-ai Tool objects) and writes Java files")
        print("through the str_replace_editor tool. Without tool_calls the")
        print("pipeline produces nothing.")
    else:
        print("GO: tool calling works — the pipeline's hard requirement is met.")
    for limit in (16000, 32768):
        if results.get("basic") and not results.get(f"max_tokens_{limit}"):
            print(f"NOTE: max_tokens={limit} rejected — patch llm_services.py before running.")
    print("=" * 60)


if __name__ == "__main__":
    main()
