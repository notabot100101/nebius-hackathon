# Nebius × NVIDIA Global AI Hackathon — Status Tracker

> Project: Trust-First Personal Agent  
> Deadline: Oct 30 2026  
> Last updated: 2026-09-30

## Phase 0 ✅ – Stack Check
- [x] API key valid (Nebius Token Factory)
- [x] Models enumerated (Nemotron family)
- [x] Chat completion works
- [x] Tool calling verified
- [x] `hello_nemotron.py` passes

## Phase 1 ✅ – Core Scaffold
- [x] `core/agent.py` — Nebius client + single-turn loop
- [x] `core/memory.py` — atomic file I/O, proof storage
- [x] `core/tools.py` — tool dispatch, verification, schemas
- [x] `core/registry.py` — skill auto-discovery
- [x] `core/config.py` — env/config loader
- [x] `agent.py` — CLI entry point (single turn + REPL)

## Phase 2 ✅ – Multi-turn History
- [x] Persistent conversation history across turns
- [x] Proper message threading for tool calls

## Phase 3 ✅ – Skill System
- [x] `@skill` decorator
- [x] Auto-discovery from `skills/*.py`
- [x] `calculator.py` — safe math evaluation
- [x] `web_search.py` — URL fetch
- [x] `system_info.py` — disk, memory, load, git status

## Phase 4 ✅ – Safety Hardening
- [x] Path traversal blocked
- [x] Dangerous command patterns blocked
- [x] Sudo escalation blocked
- [x] Shell timeout (30s)
- [x] File read truncation (4K chars)

## Phase 5 ✅ – Reliability
- [x] Retry logic with exponential backoff (429, 502, 503, 504)
- [x] Configurable `max_retries` via env/config

## Tests ✅
| Module | Tests | Status |
|--------|-------|--------|
| test_memory.py | 7 | PASS |
| test_tools.py | 10 | PASS |
| test_skills.py | 8 | PASS |
| test_agent.py | 3 | PASS |
| **Total** | **28** | **PASS** |

## Demos ✅
- [x] `scripts/hello-agent.py` — single-turn agent
- [x] `scripts/hello_nemotron.py` — stack health check
- [x] Trust-First Task Manager demo (multi-turn)

## Budget / Credits
| Source | Status |
|--------|--------|
| Current balance | $0.98 trial / $29.75 paid |
| Code `NEBIUS-DEVPOST-GLOBAL26` ($25) | ❌ Blocked — Cloudflare on console |
| Builders Program ($25) | ❌ Blocked — same console, no API endpoint found |

## Deliverables Created (2026-09-30)
| File | Purpose |
|---|---|
| `docs/devpost-copy-paste-ready.md` | **Copy-paste-ready Devpost submission** — maps every field (Name, Tagline, About, Built With, Try It Out, REQUIRED Platform Feedback) |
| `docs/demo-recording-checklist.md` | **Scene-by-scene recording checklist** — pre-recording setup, 6 scenes, B-roll, export settings, one-page cheat sheet |
| `../../.openclaw/workspace/nebius-hackathon-status-2026-09-30.md` | Master combined status (this doc + all prior threads) |

## Next Steps (Pending — Paul-Only)
- [ ] **Record demo video** — use `docs/demo-recording-checklist.md` (~2:40 target)
- [ ] **Upload video** to YouTube — keep link handy for Devpost
- [ ] **Create GitHub repo** — push `~/nebius-hackathon` public, paste URL into Devpost
- [ ] **Create Devpost project page** — log in as `ultramarine963`, paste copy from `docs/devpost-copy-paste-ready.md`
- [ ] **Credit redemption** — manual login to console.nebius.com (Cloudflare blocks automation)

## Blockers
1. **No GitHub remote** — repo is local only. Paul must create public repo and push.
2. **No demo video recorded** — agent cannot record video. Script + checklist ready.
3. **Devpost login redirect** — browser automation blocked by CDP origin rejection. Paul must log in manually.
4. **Cloudflare CAPTCHA** on console.nebius.com prevents automated credit redemption. Paul must redeem promo code manually.
5. **No billing API** — credit checks require console login.
