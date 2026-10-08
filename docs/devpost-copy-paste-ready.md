# Trust-First Personal Agent — Devpost Copy-Paste Sheet
> For: Nebius × NVIDIA Global AI Hackathon (Personal AI track)
> Project page: https://nebius-x-nvidia-global-ai-hackathon.devpost.com/
> Deadline: Oct 30 2026
>
> Instructions for Paul: Open your Devpost project creation page. Copy the
> text under each heading below straight into the matching Devpost field.

---

## Devpost Field: Project Name

```
Trust-First Personal Agent
```

---

## Devpost Field: One-Liner / Tagline

```
An always-on personal assistant that refuses to claim success until it can prove the world actually changed.
```

---

## Devpost Field: About / Story (the main description)

### The Problem

Personal AI agents are getting smarter — but they still lie, hallucinate facts, and report success for work they never actually did. You ask an agent to "write a summary to demo/summary.md," and it cheerfully replies, "Done!" while the file is empty or missing. Without proof, you can't trust an autonomous assistant with anything that matters.

### How It Works

**Trust-First Personal Agent** flips the script: *every action is checked before you ever see the answer.*

1. You send a prompt to the agent.
2. The model (NVIDIA Nemotron via Nebius Token Factory) decides which tools to call — `read_file`, `write_file`, `list_dir`, `run_command`, `calculate`.
3. Each tool call is executed locally, then **verified**:
   - Write a file → read it back and confirm the bytes match.
   - Run a command → capture return code, stdout, and stderr.
   - Calculate → evaluate the expression and store the exact result.
4. Only after verification succeeds does the agent report success.
5. Every verified claim is stored as a dated JSON fact in `memory/long_term/facts/`.

### Architecture

- **NebiusClient** (`core/agent.py`) — stdlib-only OpenAI-compatible client for Nebius Token Factory.
- **ToolExecutor** (`core/tools.py`) — dispatches tool calls, returns `ToolResult` with `success`, `proof_claim`, and `proof_evidence`.
- **Memory** (`core/memory.py`) — atomic file I/O, path-traversal blocking, and persistent proof storage.
- **Registry** (`core/registry.py`) — auto-discovers custom skills from `skills/*.py`.
- **Safety** — command timeouts (30s), path traversal blocked, irreversible actions logged.

### Try It in 30 Seconds

```bash
python3 scripts/demo_task_manager.py
```

The demo reads 10 tasks (3 done, 7 pending), uses the calculate tool for 30.0%, writes `demo/summary.md`, verifies the summary exists and contains the expected briefing fields, and stores the proof chain in `demo-task-manager-result.json`. You can inspect every claim.

### What's Next

- **Multi-turn planning** — decompose complex goals into verified sub-tasks.
- **Long-term memory search** — semantic + keyword retrieval across proof logs.
- **Human-in-the-loop gates** — reversible ops auto-approved, irreversible ops await approval.
- **OpenClaw integration** — run as a persistent background agent with cron-triggered turns.

---

## Devpost Field: Built With / Tech Stack

Paste this as a comma-separated or bulleted list:

- Nebius Token Factory
- NVIDIA Nemotron 3 family (Nano 30B, Lightning, Super 120B, Ultra 550B)
- Python 3.10+ standard library
- Atomic file I/O (tempfile + os.replace)
- Plain-file JSON memory
- OpenClaw agent runtime

License: Apache-2.0

---

## Devpost Field: Try It Out / Links

- GitHub repo: https://github.com/notabot100101/nebius-hackathon
- Demo video: *(paste your YouTube/Vimeo link here once recorded)*

> ⚠️ **To do before submission:**
> 1. Record the 2–3 min demo video.
> 2. Upload the video to YouTube (unlisted or public) and paste the link here.
> 3. Paste the final video link into Devpost and submit after Paul's final approval.

---

## Devpost Field: Platform Feedback — REQUIRED

> ⚠️ **This hackathon requires feedback on Nebius tools and NVIDIA models as part of every submission.**

### What Worked Well

**Nebius Token Factory** → Blazing fast, OpenAI-compatible inference. We ran the entire agent loop — tool-calling, proof verification, and final answer — on NVIDIA Nemotron-3-Nano-30B-A3B with sub-second latency. The stdlib-only integration (`urllib.request`) took under 30 lines to get a working chat client.

**Nemotron-3-Nano-30B-A3B** → Surprisingly capable for a "Nano" model. It consistently produced correct JSON tool-call arguments across read, write, calculate, and run_command. We used it as the default because it is fast, cheap, and accurate enough for 90% of tasks.

**Model Fallbacks** → The Nebius model catalog let us tier quality vs cost:
- Nano 30B for everyday tool loops
- Lightning for latency-sensitive turns
- Super 120B for complex multi-step reasoning
- Ultra 550B for critical or ambiguous prompts

**Python stdlib-only stack** → Because Nebius serves standard OpenAI-format `/chat/completions`, we needed zero SDK dependencies. This made the project instantly portable and dependency-free.

### What Could Be Improved

**1. No billing/credit API endpoint** — The inference API has no way to query remaining credits programmatically. We had to guess usage from token counts. A simple `GET /billing/credits` endpoint would let agents self-monitor spend.

**2. Console login blocked by Cloudflare** — `console.nebius.com` and `tokenfactory.nebius.com` login pages are behind aggressive anti-bot protection. This makes it impossible to apply promo codes or check credit status via browser automation, forcing manual OAuth login every time.

**3. Inconsistent model naming** — The model catalog uses a mix of slash separators (`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`), underscores (`nvidia/Nemotron-3_5-Lightning`), and lowercase variants (`nvidia/nemotron-3-super-120b-a12b`). A single canonical naming convention would reduce copy-paste errors in automation.

**4. Promo code workflow** — The Devpost promo code (`NEBIUS-DEVPOST-GLOBAL26`) required manual form submission and manual console redemption. An API or CLI path to apply codes would streamline hackathon onboarding.

**5. Builder Program ambiguity** — The AI Builder Program signup at `dev.nebius.com/builders` is a HubSpot form. We could not confirm enrollment status programmatically, and the welcome email was indistinguishable from a marketing newsletter. A clear enrollment confirmation with credit details attached would help.

---

## Quick Reference Table

| Devpost Field | What to Paste / Status |
|---|---|
| Project Name | `Trust-First Personal Agent` ✅ Ready |
| Tagline | `An always-on personal assistant that refuses to claim success until it can prove the world actually changed.` ✅ Ready |
| About / Story | Sections above (Problem → How It Works → Architecture → Demo → What's Next) ✅ Ready |
| Built With | Nebius Token Factory, NVIDIA Nemotron, Python stdlib, OpenClaw ✅ Ready |
| Try It Out / Links | GitHub repo ✅ ready; demo video ⚠️ needs Paul to record/upload |
| Platform Feedback | Sections above (What Worked + What Could Improve) ✅ Ready |
| Video | 2–3 min demo ⚠️ Needs recording |

---

*Prepared 2026-09-30 for Paul / Ultramarine963 — combine with pitch-script-final.md and STATUS.md*
