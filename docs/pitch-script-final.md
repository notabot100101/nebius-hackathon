# Trust-First Personal Agent — Pitch Script (Final)

A polished spoken demo script for a 2–3 minute hackathon pitch video.
Target length: ~2:40. Speak at natural pace — ~130–150 words per minute.

---

## Setup Notes

- **Visual:** Split-screen. Presenter on left (~30%). Terminal fullscreen on right (~70%).
- **Terminal font:** Large (18–20pt), high contrast, no terminal transparency.
- **Have ready:** `demo/todo.txt` and `hello-agent-result.json` open in adjacent tabs.
- **Practice the one-liner twice** before recording. It must be fluid.

---

## Hook (0:00 – 0:20)

> "What if your AI assistant couldn't fib?"
>
> "You ask it to write a file, run a command, calculate a number — and instead of just saying 'Done,' it proves it. Today I'm showing you Trust-First Personal Agent, built for the Nebius × NVIDIA Global AI Hackathon. Every tool call is verified before you ever see the answer."

**Presenter note:** Look at camera on "What if…", then gesture toward terminal on "built for the Nebius × NVIDIA hackathon." Energy: curious, not salesy.

---

## Problem (0:20 – 0:45)

> "Here's the frustration: agents hallucinate success. You ask an assistant to create a summary file, and it replies, 'Done!' But the file is empty. Or missing. Or the math is wrong."
>
> "Without proof, you can't trust automation with real work. You end up double-checking everything instead of actually delegating."
>
> "We fix that by making proof the default — not an afterthought."

**Presenter note:** Slight head shake on "empty. Or missing." Pause after "delegating." Let the problem land.

---

## Demo Walkthrough (0:45 – 2:00)

**Step 1 — One command, one proof.**

*(Type into terminal — practice this line until muscle memory)*

```bash
python3 scripts/hello-agent.py "Read demo/todo.txt, count done vs pending tasks, compute completion percent, and write a briefing to demo/summary.md"
```

> "The prompt goes to NVIDIA Nemotron, served through Nebius Token Factory. The model decides which tools to call: `read_file`, `calculate`, `write_file`."

**Step 2 — Watch the tool calls live.**

> "First, `read_file` on `demo/todo.txt`. The agent counts 10 total tasks: 3 done, 7 pending. Then `calculate` runs `(3 / 10) * 100` — result: `30.0%`."
>
> "Then `write_file` creates `demo/summary.md`. But here's the twist: after writing, the agent immediately runs `read_file` on the same path and compares bytes. Expected 271 bytes, actual 271 bytes, match confirmed. Only then does it say success."

**Step 3 — Inspect the proof chain.**

*(Switch to `hello-agent-result.json` — zoom in so JSON is readable)*

> "Every step is logged: tool name, claim, evidence — exact bytes, return codes, expressions. You own the proof. It's plain JSON you can read, audit, or version-control."

**Presenter note:** Keep eyes on terminal during demo. Don't narrate every line — highlight the *verification* moments. Point at the byte-match line specifically.

---

## Trust-First Reveal (2:00 – 2:30)

> "This isn't just logging. It's verification at the point of action. The agent refused to report success until the file actually existed and matched."
>
> "If the write had silently failed — disk full, permission denied, wrong path — the agent would have caught it and reported failure instead of lying to you."
>
> "That's the difference between 'I think I did it' and 'I proved I did it.'"

**Presenter note:** This is the money line. Slow down. Make eye contact with camera on "I proved I did it."

---

## Closing / Take 3 (2:30 – 3:00)

> "Trust-First Personal Agent runs on Python stdlib only — zero pip dependencies. It uses Nebius Token Factory for fast, cheap Nemotron inference. The memory is plain files you own. The skills are auto-discoverable Python modules. And the proof is undeniable."
>
> "You can run the demo right now from the repo. Every command, every claim, every byte — verified."
>
> *(Presenter smiles, gestures to GitHub / Devpost link that appears on screen)*
>
> "Trust, but verify. Or better yet — just verify."

**Presenter note:** End on a slight nod. Hold the smile for 2 seconds after the last line before cutting.

---

## Optional: B-Roll / Supplemental Shots

If recording extra footage, capture:

1. **Close-up of terminal scrolling** during the `hello-agent.py` run (sped up 1.5× if needed).
2. **Static shot of `hello-agent-result.json`** opened in VS Code with syntax highlighting — zoom into the `verification` block.
3. **Wide shot of presenter + screen** for the opening hook and closing line.
4. **Text overlay** at end: GitHub repo URL + Devpost project URL.

---

## Timing Checklist

| Section | Target | Word Count |
|---------|--------|------------|
| Hook | 0:00–0:20 | ~40 |
| Problem | 0:20–0:45 | ~60 |
| Demo Walkthrough | 0:45–2:00 | ~160 |
| Trust-First Reveal | 2:00–2:30 | ~65 |
| Closing | 2:30–3:00 | ~75 |
| **Total** | **~2:40** | **~400** |

---

*End of script.*
