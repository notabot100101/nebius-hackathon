# Nebius × NVIDIA Hackathon – Proof-First Personal Agent

> Status tracker for the Personal AI track entry.  
> Devpost deadline: **30 Oct 2026** | Internal deadline: **28 Oct 2026**

## Current State

**Last updated:** 2026-09-23 18:11 UTC+2  
**Latest commit:** `328a32f` Phase 5: Integration tests, skill fixes, safety verification

## Completed Phases

| Phase | Status | Commit | Notes |
|-------|--------|--------|-------|
| 0: Stack check | ✅ | `735e24d` | API key, model list, chat, tool-calling verified |
| 1: Scaffold | ✅ | `77fa601` | Core modules, tests, README, architecture doc |
| 2: Multi-turn history | ✅ | `a4b375a` | Agent maintains conversation history across turns |
| 3: Skill system | ✅ | `a4b375a` | `@skill` decorator, auto-discovery from `skills/` |
| 4: Safety hardening | ✅ | `a4b375a` | Block sudo, dangerous patterns, disk destroyers |
| 5: Tests + verification | ✅ | `328a32f` | 24 tests pass (7 memory + 10 tools + 7 skills) |

## Test Results

```
Memory module tests:     7 passed, 0 failed
Tools module tests:     10 passed, 0 failed
Skills & Safety tests:   7 passed, 0 failed
```

## Architecture

```
nebius-hackathon/
├── core/
│   ├── __init__.py       # Exports
│   ├── config.py         # Env/config loader (stdlib only)
│   ├── memory.py         # File-based persistence (atomic writes)
│   ├── tools.py          # Tool implementations + executor + schemas
│   ├── registry.py       # Skill discovery & @skill decorator
│   └── agent.py          # NebiusClient + multi-turn Agent
├── skills/
│   ├── __init__.py
│   ├── calculator.py     # Safe math evaluation (AST whitelist)
│   └── web_search.py     # URL fetch (urllib, stdlib only)
├── tests/
│   ├── test_memory.py    # 7 tests
│   ├── test_tools.py     # 10 tests
│   └── test_skills.py    # 7 tests
├── scripts/
│   ├── hello_nemotron.py # Phase 0: API health check
│   └── hello-agent.py    # Phase 1: one full agent turn
├── docs/
│   └── architecture.md   # Design doc
└── README.md
```

## Key Features

- **Proof-first**: Every tool returns `ToolResult` with `proof_claim` + `proof_evidence`
- **Multi-turn**: Agent maintains `self.history` across `run_turn()` calls
- **Skill system**: `@skill` decorator + auto-discovery from `skills/*.py`
- **Safety**: Path traversal blocking, command timeout (30s), sudo/dangerous pattern rejection
- **Stdlib only**: No pip install required (Python 3.10+)

## Next Steps (Post-Resume)

1. **Multi-turn REPL** – Test interactive mode in `agent.py`
2. **Memory search** – Add semantic/keyword search over stored proofs
3. **More skills** – File organizer, git helper, system monitor
4. **Error recovery** – Retry with fallback models on API errors
5. **Devpost submission** – Demo video, project page

## Blockers

None. All phases complete and tested.
