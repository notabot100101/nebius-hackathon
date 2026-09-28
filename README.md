# Proof-First Personal Agent

> Built for the **Nebius × NVIDIA Global AI Hackathon** (Personal AI track).  
> Deadline: Oct 30 2026 · [Devpost page](https://nebius-x-nvidia-global-ai-hackathon.devpost.com/)

An always-on personal assistant whose defining feature is that it **verifies its own work**:
after every action it checks that the world actually changed (file written, command succeeded, expected output present) and refuses to report success it cannot prove.

- **Reasoning**: NVIDIA Nemotron models served via **Nebius Token Factory**
- **Memory**: plain files you own, read, and edit
- **Safety**: capability whitelist, path-traversal blocking, command timeouts, proof logging

## Live demo (30 seconds)

```bash
# One command, one proof
python3 scripts/hello-agent.py \
  "Read demo/todo.txt, count done vs pending tasks, compute completion %, and write a briefing to demo/summary.md"
```

The agent will read the file, calculate 30.0 % completion, write the summary, read it back to verify the bytes match, store the proof, and report the result — all with full JSON trace.

## Quick start

```bash
# 1. API key from https://tokenfactory.nebius.com
export NEBIUS_API_KEY=...                 
# …or put it in ~/.openclaw/secrets/nebius.env

# 2. Stack health check
python3 scripts/hello_nemotron.py

# 3. One full agent turn
python3 scripts/hello-agent.py "List files in /tmp and tell me how many"
```

The agent sends your prompt to Nemotron, lets the model choose tools, executes each one with proof verification, stores successful claims in `~/.nebius-hackathon/memory/`, and returns a final answer plus `hello-agent-result.json`.

## Architecture

```
core/
  memory.py    – Atomic file I/O, state, proof storage
tools.py       – Tool dispatch, verification, JSON schemas for LLM
registry.py    – Skill discovery from skills/*.py
agent.py       – Nebius client + single-turn loop
```

Every tool returns a `ToolResult` with:
- `success` — did it work?
- `proof_claim` — human-readable assertion
- `proof_evidence` — structured data (path, bytes, returncode, match…)

Successful claims are stored before the user ever sees the answer.

## Dependencies

- Python 3.10+
- Standard library only (`json`, `urllib.request`, `subprocess`, `pathlib`, …)
- No pip install required.

## Local testing (no API key)

```bash
python3 tests/test_memory.py   # 7 tests
python3 tests/test_tools.py    # 10 tests
python3 tests/test_agent.py    # 3 tests
```

## Project structure

```
nebius-hackathon/
├── core/           # Agent engine (stdlib + urllib only)
├── skills/         # Auto-discoverable skill modules
├── tests/          # Unit tests
├── scripts/        # Entry points
│   ├── hello_nemotron.py
│   └── hello-agent.py
├── docs/
│   └── architecture.md
├── README.md
└── LICENSE
```

## Models

| Model | Role |
|-------|------|
| `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | Primary — fast, cheap, tool-capable |
| `nvidia/Nemotron-3_5-Lightning` | Speed fallback |
| `nvidia/nemotron-3-super-120b-a12b` | Stronger reasoning |
| `nvidia/Nemotron-3-Ultra-550b-a55b` | Highest quality |

Set via `MODEL_ID` env var.

## Safety

- Path traversal blocked
- Shell commands capped at 30 s
- Irreversible actions logged; automated only for reversible ops
- Full proof trail in `memory/long_term/facts/`

## License

Apache-2.0 (see LICENSE).
