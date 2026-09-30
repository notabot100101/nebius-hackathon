#!/usr/bin/env python3
"""Phase-0 go/no-go for the Nebius x NVIDIA hackathon entry.

Checks, against the live Nebius Token Factory API (OpenAI-compatible):
  1. the API key works and which NVIDIA models are actually served,
  2. one plain chat completion with a Nemotron model,
  3. whether tool/function calling works (an agent needs it).
Standard library only. The key is read from $NEBIUS_API_KEY or from
~/.openclaw/secrets/nebius.env (line: NEBIUS_API_KEY=...) and is never printed.
Writes a key-free summary to phase0-result.json.
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

BASE = "https://api.tokenfactory.nebius.com/v1"
SECRET_FILE = Path.home() / ".openclaw/secrets/nebius.env"


def load_key():
    key = os.environ.get("NEBIUS_API_KEY", "").strip()
    if not key and SECRET_FILE.exists():
        for line in SECRET_FILE.read_text().splitlines():
            if line.strip().startswith("NEBIUS_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    return key


def call(path, key, payload=None):
    req = urllib.request.Request(BASE + path, method="POST" if payload else "GET",
                                 data=json.dumps(payload).encode() if payload else None,
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode(errors="replace")[:500]}


def content_to_text(content):
    """Normalize message.content from string or typed parts into plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                text = part.get("text") or part.get("content")
                if isinstance(text, str):
                    parts.append(text)
                elif text is not None:
                    parts.append(str(text))
        return "".join(parts)
    return str(content)


def pick_nemotron(ids):
    nem = [i for i in ids if "nemotron" in i.lower()]
    for pref in ("nano", "super", "ultra"):          # cheapest capable first
        for i in nem:
            if pref in i.lower():
                return i, nem
    return (nem[0] if nem else None), nem


def main():
    key = load_key()
    if not key:
        sys.exit(f"NO KEY: set NEBIUS_API_KEY or put 'NEBIUS_API_KEY=...' into {SECRET_FILE} (chmod 600).")
    res = {"checked_at": time.strftime("%Y-%m-%d %H:%M:%S"), "base": BASE}

    st, models = call("/models", key)
    res["models_http"] = st
    ids = [m.get("id") for m in models.get("data", [])] if st == 200 else []
    res["nvidia_models"] = sorted(i for i in ids if i and i.lower().startswith("nvidia/"))
    model, nem = pick_nemotron(ids)
    res["nemotron_models"], res["chosen_model"] = nem, model
    print(f"/models HTTP {st}: {len(ids)} models, {len(nem)} Nemotron -> using {model}")
    if st != 200 or not model:
        json.dump(res, open("phase0-result.json", "w"), indent=2)
        sys.exit("NO-GO: key rejected or no Nemotron model served (see phase0-result.json)")

    st, out = call("/chat/completions", key, {"model": model, "max_tokens": 256, "temperature": 0, "messages": [
        {"role": "user", "content": "Reply with exactly: NEMOTRON-OK"}]})
    raw_content = (out.get("choices") or [{}])[0].get("message", {}).get("content", "") if st == 200 else ""
    txt = content_to_text(raw_content)
    res["chat_http"], res["chat_ok"] = st, "NEMOTRON-OK" in (txt or "")
    print(f"chat HTTP {st}: {'OK' if res['chat_ok'] else 'unexpected reply'} ({(txt or out)!s:.80})")

    tool = {"type": "function", "function": {"name": "write_file", "description": "Write text to a file",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"},
                           "text": {"type": "string"}}, "required": ["path", "text"]}}}
    # Note: forced tool_choice is not supported by all Nemotron models;
    # we test natural tool calling by providing tools and a prompt that needs one.
    st, out = call("/chat/completions", key, {"model": model, "max_tokens": 200, "tools": [tool],
        "messages": [{"role": "user", "content": "Use the write_file tool to save the text 'hello' into notes.txt."}]})
    calls = (out.get("choices") or [{}])[0].get("message", {}).get("tool_calls") if st == 200 else None
    res["tools_http"], res["tool_calling_ok"] = st, bool(calls)
    print(f"tool-calling HTTP {st}: {'OK ' + calls[0]['function']['name'] if calls else 'NOT used in this sample (may still work in agent mode)'}")

    json.dump(res, open("phase0-result.json", "w"), indent=2)
    go = res["chat_ok"] and res["tool_calling_ok"]
    print("\nGO: stack works for an agent." if go else "\nPARTIAL: see phase0-result.json")
    sys.exit(0 if go else 2)


if __name__ == "__main__":
    main()
