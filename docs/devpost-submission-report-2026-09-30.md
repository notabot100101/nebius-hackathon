# Devpost Submission Report — 2026-09-30

**Status:** SUPERSEDED BY 2026-10-08 READINESS SWEEP — see `docs/submission-readiness-2026-10-08.md`.

2026-10-08 update: the GitHub repo now exists and is public at `https://github.com/notabot100101/nebius-hackathon`. Devpost login, demo video upload, and final submit still require Paul's explicit approval.

Original 2026-09-30 status: BLOCKED — Login required before submission can proceed
**Hackathon:** Nebius × NVIDIA Global AI Hackathon
**Devpost Account:** (redacted - see ops notes)

---

## What Was Tried

### 1. Connected to Paul's Chrome
- Connected to Chrome via the OpenClaw browser tool (CDP port 18800)
- 3 tabs open: Devpost hackathon page, Devpost hackathons list, Devpost login page
- None of the tabs showed a logged-in Devpost session

### 2. Attempted Google OAuth Login
- Clicked "Log in with Google" on Devpost
- Google showed the account chooser
- **BLOCKED:** After selecting the account, Google rejected the sign-in with:
  > "This browser or app may not be secure."
- This is a known anti-automation measure for CDP-driven browsers

### 3. Attempted GitHub OAuth Login
- Clicked "Log in with GitHub" on Devpost
- GitHub login page loaded
- **BLOCKED:** No GitHub credentials known; could not proceed

### 4. Attempted Email/Password Login
- Checked if Chrome had saved Devpost credentials → none found
- No autofill suggestions appeared in the email field
- **BLOCKED:** Password unknown

### 5. Checked Alternative Chrome Profiles
- OpenClaw managed profile: works, no logged-in sessions
- Chrome extension profile: not connected
- Chrome MCP user profile (existing-session): could not connect — no DevToolsActivePort file at `~/.config/google-chrome/DevToolsActivePort`
- Paul's actual `google-chrome --remote-debugging-port=9222` process was not detected running

### 6. Checked Deliverable Status
- **GitHub repo:** Local only (`git remote -v` returned empty) → still needs to be pushed public
- **Demo video:** No `.mp4`/`.mov`/`.webm` files found in the project directory → still needs recording/upload

---

## Known Blockers (Confirmed)

| # | Blocker | Status |
|---|---------|--------|
| 1 | **GitHub repo** — public at `https://github.com/notabot100101/nebius-hackathon` as of 2026-10-08 | RESOLVED |
| 2 | **No demo video** — not yet recorded | STILL ACTIVE |
| 3 | **Devpost login** — browser automation blocked by Google/GitHub security | CONFIRMED — Paul must log in manually |
| 4 | **Cloudflare on Nebius console** — credit redemption requires manual login | STILL ACTIVE |

---

## Ready-to-Paste Devpost Submission Copy

Once Paul manually logs into Devpost, the following copy can be pasted directly into each field.

### Project Name
```
Trust-First Personal Agent
```

### Tagline / One-Liner
```
An always-on personal assistant that refuses to claim success until it can prove the world actually changed.
```

### About / Story（full description）

**The Problem**

Personal AI agents are getting smarter — but they still lie, hallucinate facts, and report success for work they never actually did. You ask an agent to "write a summary to demo/summary.md," and it cheerfully replies, "Done!" while the file is empty or missing. Without proof, you can't trust an autonomous assistant with anything that matters.

**How It Works**

Trust-First Personal Agent flips the script: *every action is checked before you ever see the answer.*

1. You send a prompt to the agent.
2. The model (NVIDIA Nemotron via Nebius Token Factory) decides which tools to call — `read_file`, `write_file`, `list_dir`, `run_command`, `calculate`.
3. Each tool call is executed locally, then **verified**:
   - Write a file → read it back and confirm the bytes match.
   - Run a command → capture return code, stdout, and stderr.
   - Calculate → evaluate the expression and store the exact result.
4. Only after verification succeeds does the agent report success.
5. Every verified claim is stored as a dated JSON fact in `memory/long_term/facts/`.

**Architecture**

- **NebiusClient** (`core/agent.py`) — stdlib-only OpenAI-compatible client for Nebius Token Factory.
- **ToolExecutor** (`core/tools.py`) — dispatches tool calls, returns `ToolResult` with `success`, `proof_claim`, and `proof_evidence`.
- **Memory** (`core/memory.py`) — atomic file I/O, path-traversal blocking, and persistent proof storage.
- **Registry** (`core/registry.py`) — auto-discovers custom skills from `skills/*.py`.
- **Safety** — command timeouts (30s), path traversal blocked, irreversible actions logged.

**Try It in 30 Seconds**

```bash
python3 scripts/demo_task_manager.py
```

The agent reads 10 tasks (3 done, 7 pending), calculates 30.0%, writes `demo/summary.md`, reads it back to verify the bytes match, and stores the proof chain in `hello-agent-result.json`. You can inspect every claim.

**What's Next**

- **Multi-turn planning** — decompose complex goals into verified sub-tasks.
- **Long-term memory search** — semantic + keyword retrieval across proof logs.
- **Human-in-the-loop gates** — reversible ops auto-approved, irreversible ops await approval.
- **OpenClaw integration** — run as a persistent background agent with cron-triggered turns.

### Built With / Tech Stack
```
- Nebius Token Factory
- NVIDIA Nemotron 3 family (Nano 30B, Lightning, Super 120B, Ultra 550B)
- Python 3.10+ standard library
- Atomic file I/O (tempfile + os.replace)
- Plain-file JSON memory
- OpenClaw agent runtime
```
License: Apache-2.0

### Try It Out / Links
- GitHub repo: https://github.com/notabot100101/nebius-hackathon
- Demo video: *(paste your YouTube/Vimeo link here once recorded)*

### Platform Feedback — REQUIRED

**What Worked Well**

**Nebius Token Factory** → Blazing fast, OpenAI-compatible inference. We ran the entire agent loop — tool-calling, proof verification, and final answer — on NVIDIA Nemotron-3-Nano-30B-A3B with sub-second latency. The stdlib-only integration (`urllib.request`) took under 30 lines to get a working chat client.

**Nemotron-3-Nano-30B-A3B** → Surprisingly capable for a "Nano" model. It consistently produced correct JSON tool-call arguments across read, write, calculate, and run_command. We used it as the default because it is fast, cheap, and accurate enough for 90% of tasks.

**Model Fallbacks** → The Nebius model catalog let us tier quality vs cost:
- Nano 30B for everyday tool loops
- Lightning for latency-sensitive turns
- Super 120B for complex multi-step reasoning
- Ultra 550B for critical or ambiguous prompts

**Python stdlib-only stack** → Because Nebius serves standard OpenAI-format `/chat/completions`, we needed zero SDK dependencies. This made the project instantly portable and dependency-free.

**What Could Be Improved**

1. **No billing/credit API endpoint** — The inference API has no way to query remaining credits programmatically. We had to guess usage from token counts. A simple `GET /billing/credits` endpoint would let agents self-monitor spend.

2. **Console login blocked by Cloudflare** — `console.nebius.com` and `tokenfactory.nebius.com` login pages are behind aggressive anti-bot protection. This makes it impossible to apply promo codes or check credit status via browser automation, forcing manual OAuth login every time.

3. **Inconsistent model naming** — The model catalog uses a mix of slash separators (`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`), underscores (`nvidia/Nemotron-3_5-Lightning`), and lowercase variants (`nvidia/nemotron-3-super-120b-a12b`). A single canonical naming convention would reduce copy-paste errors in automation.

4. **Promo code workflow** — The Devpost promo code (`NEBIUS-DEVPOST-GLOBAL26`) required manual form submission and manual console redemption. An API or CLI path to apply codes would streamline hackathon onboarding.

5. **Builder Program ambiguity** — The AI Builder Program signup at `dev.nebius.com/builders` is a HubSpot form. We could not confirm enrollment status programmatically, and the welcome email was indistinguishable from a marketing newsletter. A clear enrollment confirmation with credit details attached would help.

---

## Next Steps for Paul

1. **Log into Devpost manually** in Chrome (use Google OAuth at https://devpost.com/users/login)
2. **Navigate to:** https://nebiusglobalaihackathon.devpost.com/
3. **Click "My projects" → "Join hackathon" (if not already registered)**
4. **Create new project** and paste the above copy into each field
5. **Push repo to GitHub** and paste the public URL into "Try It Out"
6. **Record demo video** (~2–3 min) using `docs/demo-recording-checklist.md`
7. **Upload video to YouTube** and paste the link
8. **Submit the project**

Once logged in, this subagent can be re-run to automate the form-filling portion of the submission.

---

*Report generated by subagent — 2026-09-30*
