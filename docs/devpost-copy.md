# Trust-First Personal Agent

## The Problem

Personal AI agents are getting smarter — but they still lie, hallucinate facts, and report success for work they never actually did. You ask an agent to "write a summary to `demo/summary.md`," and it cheerfully replies, "Done!" while the file is empty or missing. Without proof, you can't trust an autonomous assistant with anything that matters.

## How It Works

**Trust-First Personal Agent** flips the script: *every action is checked before you ever see the answer.*

1. You send a prompt to the agent.
2. The model (NVIDIA Nemotron via Nebius Token Factory) decides which tools to call — `read_file`, `write_file`, `list_dir`, `run_command`, `calculate`.
3. Each tool call is executed locally, then **verified**:
   - Write a file → read it back and confirm the bytes match.
   - Run a command → capture return code, stdout, and stderr.
   - Calculate → evaluate the expression and store the exact result.
4. Only after verification succeeds does the agent report success.
5. Every verified claim is stored as a dated JSON fact in `memory/long_term/facts/`.

## Architecture

- **NebiusClient** (`core/agent.py`) — stdlib-only OpenAI-compatible client for Nebius Token Factory.
- **ToolExecutor** (`core/tools.py`) — dispatches tool calls, returns `ToolResult` with `success`, `proof_claim`, and `proof_evidence`.
- **Memory** (`core/memory.py`) — atomic file I/O, path-traversal blocking, and persistent proof storage.
- **Registry** (`core/registry.py`) — auto-discovers custom skills from `skills/*.py`.
- **Safety** — command timeouts (30s), path traversal blocked, irreversible actions logged.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Inference | **Nebius Token Factory** — OpenAI-compatible API with NVIDIA Nemotron models (30B Nano default, up to 550B Ultra) |
| Models | **NVIDIA Nemotron 3 family** — fast, cheap, tool-capable reasoning |
| Agent runtime | **OpenClaw** — local Python 3.10+, stdlib only, zero pip dependencies |
| Memory | Plain JSON files you own, read, and edit |
| Proof | Atomic verification + dated fact storage |

## Trust-First in Action

Run the 30-second demo:

```bash
python3 scripts/hello-agent.py "Read demo/todo.txt, count done vs pending, compute completion %, and write a briefing to demo/summary.md"
```

The agent reads 10 tasks (3 done, 7 pending), calculates `30.0%`, writes `demo/summary.md`, reads it back to verify the bytes match, and stores the proof chain in `hello-agent-result.json`. You can inspect every claim.

## What's Next

- **Multi-turn planning** — decompose complex goals into verified sub-tasks.
- **Long-term memory search** — semantic + keyword retrieval across proof logs.
- **Human-in-the-loop gates** — reversible ops auto-approved, irreversible ops await approval.
- **OpenClaw integration** — run as a persistent background agent with cron-triggered turns.

Built for the **Nebius × NVIDIA Global AI Hackathon** (Personal AI track).
