# Trust-First Personal Agent — Pitch Script

A spoken demo script for a 2–3 minute video.

---

## Hook (0:00 – 0:20)

*(Camera on presenter, terminal fullscreen in split-screen)*

"What if your AI assistant couldn't fib?"

"You ask it to write a file, run a command, calculate a number — and instead of just saying 'Done,' it proves it. Today I'm showing you Trust-First Personal Agent, built for the Nebius × NVIDIA hackathon. Every tool call is verified before you ever see the answer."

---

## Problem (0:20 – 0:45)

"Here's the frustration: agents hallucinate success. You ask an assistant to create a summary file, and it replies, 'Done!' But the file is empty. Or missing. Or the math is wrong. Without proof, you can't trust automation with real work — and you spend your time double-checking instead of delegating."

"We fix that by making proof the default, not an afterthought."

---

## Demo Walkthrough (0:45 – 2:00)

**Step 1 — One command, one proof.**

*(Type into terminal)*

```bash
python3 scripts/hello-agent.py "Read demo/todo.txt, count done vs pending tasks, compute completion percent, and write a briefing to demo/summary.md"
```

"The prompt goes to NVIDIA Nemotron, served through Nebius Token Factory. The model decides which tools to call — `read_file`, `calculate`, `write_file`."

**Step 2 — Watch the tool calls.**

"First, `read_file` on `demo/todo.txt`. The agent scans the file and counts 10 total tasks, 3 done, 7 pending. Then `calculate` runs `(3 / 10) * 100` — result: `30.0%`."

**Step 3 — Write and verify.**

"Then `write_file` creates `demo/summary.md`. But here's the twist: after writing, the agent immediately runs `read_file` on the same path and compares bytes. Expected 271 bytes, actual 271 bytes, match confirmed. Only then does it say success."

**Step 4 — Inspect the proof.**

*(Open `hello-agent-result.json`)*

"Every step is logged: tool name, claim, evidence — exact bytes, return codes, expressions. You own the proof. It's stored in plain JSON you can read, audit, or version-control."

---

## Trust-First Reveal (2:00 – 2:30)

"This isn't just logging. It's verification at the point of action. The agent refused to report success until the file actually existed and matched. If the write had silently failed — disk full, permission denied, wrong path — the agent would have caught it and reported failure instead of lying."

"That's the difference between 'I think I did it' and 'I proved I did it.'"

---

## Closing / Take 3 (2:30 – 3:00)

"Trust-First Personal Agent runs on Python stdlib only — no pip install required. It uses Nebius Token Factory for fast, cheap Nemotron inference. The memory is plain files you own. The skills are auto-discoverable Python modules. And the proof is undeniable."

"You can run the demo right now from the repo. Every command, every claim, every byte — verified."

*(Presenter smiles, gestures to GitHub / Devpost link on screen)*

"Trust, but verify. Or better yet — just verify."

---

*End.*
