# Proof-First Personal Agent – Architecture

> Design doc for the Nebius × NVIDIA Global AI Hackathon (Personal AI track).

## Philosophy

Every action the agent takes is **checked and proved**:
- Write a file → read it back and verify the bytes match.
- Run a command → capture stdout, stderr, return code.
- No claim of success without evidence stored in memory.

## High-Level Flow

```
User Input
    ↓
+---------------+      +---------------+
|  Nebius API   | ←→  |  Nemotron LLM |
| (OpenAI fmt)  |      | (30B default) |
+---------------+      +---------------+
    ↓
Tool calls? ──YES──→ ToolExecutor
                         ↓
                    read_file / write_file
                    list_dir  / run_command
                         ↓
                    Proof verification
                         ↓
                    Memory store (claim + evidence)
                         ↓
                    Tool results → back to LLM
                         ↓
                    Final answer
```

## Directory Layout

```
nebius-hackathon/
├── core/
│   ├── __init__.py       # Exports
│   ├── config.py         # Env/config loader
│   ├── memory.py         # File-based persistence (atomic writes)
│   ├── tools.py          # Tool implementations + executor + schemas
│   ├── registry.py       # Skill discovery & registration
│   └── agent.py          # NebiusClient + Agent single-turn loop
├── skills/
│   └── __init__.py       # Built-in + custom skills (auto-discovered)
├── tests/
│   ├── test_memory.py    # Memory atomicity, state, proofs
│   └── test_tools.py     # Tool execution, verification, errors
├── scripts/
│   ├── hello_nemotron.py # Phase 0: API health check
│   └── hello-agent.py    # Phase 1: one full agent turn demo
├── docs/
│   └── architecture.md   # This file
└── README.md
```

## Core Components

### 1. Memory (`core/memory.py`)

Plain files the user owns:

```
memory/
├── short_term/     # Working memory / session notes
├── long_term/
│   └── facts/      # Verified claim + evidence JSON files
└── state/
    └── state.json  # Agent runtime state
```

Key properties:
- **Atomic writes**: `tempfile.mkstemp` + `os.replace`
- **Path safety**: `_resolve()` blocks traversal outside `memory/`
- **Proof storage**: `store_proof(claim, evidence)` writes a dated JSON fact file
- **State**: `get_state()` / `set_state()` for versioned JSON state

### 2. Tools (`core/tools.py`)

Available tools:

| Tool | Description | Proof |
|------|-------------|-------|
| `read_file` | Read a text file | Bytes read, file exists |
| `write_file` | Atomic write + read-back verify | Expected vs actual bytes match |
| `list_dir` | Enumerate directory | Count of items |
| `run_command` | Safe shell command (30s timeout) | Return code, stdout bytes |
| `memory_read` | Read from agent memory | Bytes read |
| `memory_write` | Write to agent memory + verify | Match bool |

`ToolExecutor`:
- `schemas()` → OpenAI function schemas for the LLM
- `execute(tool_call)` → dispatches by name, parses JSON args, runs handler
- Every handler returns a `ToolResult` with `success`, `content`, `proof_claim`, `proof_evidence`

### 3. Registry (`core/registry.py`)

- Wraps `ToolExecutor` and adds skill discovery from `skills/*.py`
- `@skill(name=..., description=..., schema=...)` decorator marks functions for auto-loading
- `get_registry()` = instantiate + scan skills directory

### 4. Agent (`core/agent.py`)

`NebiusClient`:
- Uses `urllib.request` (stdlib only)
- Calls `/chat/completions` on Nebius Token Factory
- Helpers: `extract_message`, `extract_content`, `extract_tool_calls`

`Agent.run_turn(user_input)`:
1. Build messages: `[system, user]`
2. Call model with `tools=schemas`
3. If `tool_calls` returned:
   - Append assistant message with tool_calls
   - Execute each tool → `ToolResult`
   - Store successful proofs in memory
   - Append tool result messages
   - Call model again for final answer
4. Return `AgentTurnResult` (text, tool calls, results, proof log, raw messages)

### 5. Configuration (`core/config.py`)

Loads from (in order):
1. `NEBIUS_API_KEY` environment variable
2. `~/.openclaw/secrets/nebius.env`
3. Defaults for model, base URL, memory dir, timeouts

## Tool Loop in Detail

```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_input},
]

# First inference
rsp = client.chat(messages, tools=executor.schemas())
tool_calls = client.extract_tool_calls(rsp)

if tool_calls:
    messages.append(assistant_message_with_tool_calls)
    for tc in tool_calls:
        result = executor.execute(tc)
        if result.success:
            memory.store_proof(result.proof_claim, result.proof_evidence)
        messages.append({
            "role": "tool",
            "tool_call_id": tc["id"],
            "name": tc["function"]["name"],
            "content": json.dumps(result.to_dict()),
        })
    # Second inference
    final = client.chat(messages, tools=executor.schemas())
    answer = client.extract_content(final)
else:
    answer = client.extract_content(rsp)
```

## Safety

- **Command whitelist**: No `rm -rf /`, no fork bombs. Commands run under restricted PATH.
- **Path traversal blocked**: Memory `_resolve()` rejects `../../etc/passwd`.
- **Timeout**: Shell commands capped at 30 seconds.
- **Truncation**: File reads capped at ~4000 chars to protect context window.
- **Human gate**: Irreversible actions are logged; full automation reserved for reversible ops (read, write, list).

## Testing

Run locally without API key:

```bash
python tests/test_memory.py   # 7 tests, all local
python tests/test_tools.py    # 10 tests, all local
```

Run end-to-end with API:

```bash
export NEBIUS_API_KEY=...
python scripts/hello-agent.py "List files in /tmp"
```

## License

Apache-2.0 (see `LICENSE`).
