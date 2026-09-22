# (working title) Proof-First Personal Agent

> Status: working scaffold for the **Nebius × NVIDIA Global AI Hackathon** (Personal AI track, deadline Oct 30 2026).

An always-on personal assistant whose signature feature is that it **verifies its own work**:
after every action it checks that the world actually changed (file written, command succeeded,
expected output present) and refuses to report success it cannot prove.

- **Reasoning**: NVIDIA Nemotron open models served by **Nebius Token Factory**
- **Memory**: plain files the user owns and can read or edit
- **Safety**: capability whitelist, path traversal blocking, command timeouts, proof logging

## Quick start

```bash
# 1. API key (choose one)
export NEBIUS_API_KEY=...                     # from https://tokenfactory.nebius.com
# or put it in ~/.openclaw/secrets/nebius.env

# 2. Phase 0 – stack check
python3 scripts/hello_nemotron.py

# 3. Phase 1 – one full agent turn
python3 scripts/hello-agent.py "List the files in /tmp and tell me how many there are"
```

The agent will:
1. Send your prompt to the Nemotron model.
2. Let the model decide whether to call tools (`read_file`, `list_dir`, `run_command`, etc.).
3. Execute each tool **with proof verification** (e.g., write → read-back → confirm match).
4. Store successful proofs in `~/.nebius-hackathon/memory/long_term/facts/`.
5. Return a final answer plus a JSON summary (`hello-agent-result.json`).

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full design doc.

```
core/
  memory.py    – Atomic file I/O, state, proof storage
tools.py       – Tool dispatch, verification, JSON schemas for LLM
registry.py    – Skill discovery from skills/*.py
agent.py       – Nebius API client + single-turn loop
```

### Key idea: Proof-first

Every tool returns a `ToolResult` with:
- `success` bool
- `proof_claim` – human-readable assertion
- `proof_evidence` – structured data (path, bytes, returncode, match, …)

The agent stores every successful claim in memory before telling the user it worked.

## Local testing

No API key needed:

```bash
python3 tests/test_memory.py   # 7 tests
python3 tests/test_tools.py    # 10 tests
```

## Project structure

```
nebius-hackathon/
├── core/               # Agent core (stdlib + urllib only)
├── skills/             # Auto-discoverable skill modules
├── tests/              # Unit tests
├── scripts/            # Entry points
│   ├── hello_nemotron.py
│   └── hello-agent.py
├── docs/
│   └── architecture.md
├── README.md
└── LICENSE
```

## Dependencies

- Python 3.10+
- Standard library only (`json`, `urllib.request`, `subprocess`, `pathlib`, …)
- **No pip install required.**

## Models used

| Model | Role |
|-------|------|
| `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | Primary – fast, cheap, capable of tool calling |
| `nvidia/Nemotron-3_5-Lightning` | Faster fallback |
| `nvidia/nemotron-3-super-120b-a12b` | Stronger reasoning |
| `nvidia/Nemotron-3-Ultra-550b-a55b` | Highest quality |

Set via `MODEL_ID` environment variable.

## License

Apache-2.0 (see `LICENSE`).
