# Trust-First Personal Agent — Demo Video Recording Checklist
> Goal: 2:40–3:00 minute screen-capture pitch for Devpost.
> Script reference: `docs/pitch-script-final.md`

---

## Pre-Recording Setup (do once)

- [ ] **Terminal font** bumped to 18–20 pt, high contrast, no transparency.
- [ ] **Split-screen** ready: presenter camera on left (~30%), terminal fullscreen on right (~70%).
- [ ] **Windows open and sized:**
  - Terminal tab 1: repo root (`~/nebius-hackathon`)
  - Terminal tab 2: `cat demo/todo.txt` ready to run
  - Terminal tab 3: `cat hello-agent-result.json` ready to run
  - Text editor or VS Code: `docs/architecture.md` open for stack slide
- [ ] **Nebius API key** exported or in `~/.openclaw/secrets/nebius.env`.
- [ ] **Quick smoke test:** run `python3 scripts/hello_nemotron.py` — should pass in <5 seconds.
- [ ] **Practice the demo command twice** until it is muscle memory:
  ```bash
  python3 scripts/demo_task_manager.py
  ```

---

## Scene-by-Scene Checklist

### Scene 1 — Hook (0:00–0:20)
- [ ] Camera on you.
- [ ] Say the hook line: *"What if your AI assistant couldn't fib?"*
- [ ] Gesture to terminal on *"built for the Nebius × NVIDIA hackathon."*
- [ ] Energy: curious, not salesy.

### Scene 2 — Problem (0:20–0:45)
- [ ] Slight head shake on *"empty. Or missing."*
- [ ] Pause after *"delegating."* Let the problem land.

### Scene 3 — Demo Walkthrough (0:45–2:00)
- [ ] **Type the demo command live** (do not paste — typing = authenticity).
- [ ] Narrate the three tool calls as they appear:
  - `read_file` → 10 tasks, 3 done, 7 pending
  - `calculate` → 30.0%
  - `write_file` verified repair if the model omits the write call
- [ ] **Point at the verification lines** specifically (`write_file verified`, plus external checks for heading/total/pending/percentage).
- [ ] Keep eyes on terminal; don't narrate every line.

### Scene 4 — Inspect the Proof (1:40–2:00)
- [ ] Switch to `hello-agent-result.json` tab.
- [ ] Zoom JSON so `verification` block is readable.
- [ ] Caption on screen: *"Every successful claim is a timestamped, auditable fact."*

### Scene 5 — Trust-First Reveal (2:00–2:30)
- [ ] Slow down.
- [ ] Make eye contact with camera on *"I proved I did it."* This is the money line.

### Scene 6 — Closing (2:30–3:00)
- [ ] Say the stack summary and closing line:
  - *"Trust-First Personal Agent runs on Python stdlib only — zero pip dependencies. It uses Nebius Token Factory for fast, cheap Nemotron inference. The memory is plain files you own. The skills are auto-discoverable Python modules. And the proof is undeniable."*
  - *"You can run the demo right now from the repo. Every command, every claim, every byte — verified."*
  - *"Trust, but verify. Or better yet — just verify."*
- [ ] Smile, hold for 2 seconds, then cut.

---

## B-Roll / Supplemental (optional, for editing)

Capture these as separate clips so you can splice them in:

- [ ] **Close-up of terminal scrolling** during the `hello-agent.py` run (sped up 1.5× if needed).
- [ ] **Static shot of `hello-agent-result.json`** in VS Code with syntax highlighting — zoom into the `verification` block.
- [ ] **Wide shot of you + screen** for opening hook and closing line.
- [ ] **Text overlay** at end:
  ```
  GitHub: github.com/notabot100101/nebius-hackathon
  Devpost: nebius-x-nvidia-global-ai-hackathon.devpost.com
  ```

---

## Export Settings

- Format: MP4 (H.264)
- Resolution: 1920×1080 minimum
- Audio: your voice (no music needed — Devpost prefers clear narration)
- Length: **under 3:00 minutes** (Devpost limit; aim for 2:40)
- Upload: YouTube (unlisted or public) → paste link into Devpost

---

## One-Page Cheat Sheet (tape this next to your screen)

```
HOOK     (0:00)  "What if your AI assistant couldn't fib?"
PROBLEM  (0:20)  Agents lie. You double-check everything.
DEMO     (0:45)  Type the demo command. Point at verification.
PROOF    (1:40)  Show hello-agent-result.json
REVEAL   (2:00)  "I proved I did it." ← money line
CLOSE    (2:30)  Tagline + smile + hold 2 sec
```

---

*Prepared 2026-09-30 | Script: docs/pitch-script-final.md | One-liner pre-tested ✅*
