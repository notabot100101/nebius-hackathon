#!/usr/bin/env python3
"""
demo_task_manager.py – Proof-First Daily Task Manager Demo

Demonstrates the agent reading a todo list, verifying the read,
calculating statistics with evidence, and writing a verified summary.

Usage:
    python scripts/demo_task_manager.py

Outputs:
    - demo/summary.md          – human-readable daily briefing
    - demo-task-manager-result.json – structured proof chain
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import config
from core.agent import Agent


TODO_PATH = "demo/todo.txt"
SUMMARY_PATH = "demo/summary.md"

PROMPT_STEP1 = """Read the file at {todo_path}. Report the total number of tasks, completed tasks (lines with "- [x]"), and pending tasks (lines with "- [ ]")."""

PROMPT_STEP2 = """Use the calculate tool to compute ({completed} / {total}) * 100 and round to one decimal place. Report the completion percentage."""

PROMPT_STEP3 = """Write a concise daily briefing to {summary_path} with:
- Heading: "# Daily Briefing"
- Total tasks, completed tasks, pending tasks
- Completion percentage: {percentage}%
- Top 3 pending priorities (most important first)
- A brief motivational closing line

Then read back {summary_path} to verify it was written correctly. Only report success after verifying the file exists and contains the expected heading."""


def setup_demo_files():
    demo_dir = Path("demo")
    demo_dir.mkdir(exist_ok=True)
    todo = demo_dir / "todo.txt"
    if not todo.exists():
        todo.write_text("""# Demo Todo List
- [x] Task A
- [ ] Task B
- [ ] Task C
""", encoding="utf-8")
        print(f"[Setup] Created {todo}")
    else:
        print(f"[Setup] Using existing {todo}")


def verify_summary_file():
    summary = Path(SUMMARY_PATH)
    checks = {
        "exists": summary.exists(),
    }
    if not summary.exists():
        return False, checks
    text = summary.read_text(encoding="utf-8")
    checks.update({
        "has_heading": "# Daily Briefing" in text,
        "has_total": "total" in text.lower(),
        "has_pending": "pending" in text.lower(),
        "has_percentage": "%" in text,
    })
    all_ok = all(checks.values())
    return all_ok, checks


def main():
    if not config["nebius_api_key"]:
        print("ERROR: NEBIUS_API_KEY not found.")
        print("Export it or put it in ~/.openclaw/secrets/nebius.env")
        sys.exit(1)

    setup_demo_files()

    print("=" * 60)
    print("Proof-First Task Manager Demo")
    print("=" * 60)
    print(f"Model: {config['model_id']}")
    print(f"Todo:   {TODO_PATH}")
    print(f"Output: {SUMMARY_PATH}")
    print("-" * 60)

    agent = Agent()
    turn_results = []

    # ---- STEP 1: Read todo ----
    prompt1 = PROMPT_STEP1.format(todo_path=TODO_PATH)
    print(f"\n📝 Step 1 – Prompt: {prompt1[:60]}...")
    result1 = agent.run_turn(prompt1)
    turn_results.append(result1)
    print(f"Agent: {result1.assistant_text[:200]}")

    # Parse counts from the agent's response (fallback to manual count)
    total = completed = pending = None
    import re
    nums = re.findall(r"(\d+)", result1.assistant_text)
    if len(nums) >= 3:
        # Heuristic: first three numbers are total, completed, pending
        total, completed, pending = map(int, nums[:3])
    else:
        # Manual fallback
        print("\n   (Model did not return clear counts; falling back to manual parse)")
        text = Path(TODO_PATH).read_text(encoding="utf-8")
        total = len(re.findall(r"^- \[", text, re.MULTILINE))
        completed = len(re.findall(r"^- \[x\]", text, re.MULTILINE))
        pending = len(re.findall(r"^- \[ \]", text, re.MULTILINE))
    print(f"   Parsed counts – total={total}, completed={completed}, pending={pending}")

    # ---- STEP 2: Calculate percentage ----
    prompt2 = PROMPT_STEP2.format(completed=completed, total=total)
    print(f"\n🧮 Step 2 – Prompt: {prompt2[:60]}...")
    result2 = agent.run_turn(prompt2)
    turn_results.append(result2)
    print(f"Agent: {result2.assistant_text[:200]}")
    # Use the actual calculate tool result, falling back to manual compute
    calculate_result = None
    for tr in result2.tool_results:
        if tr.success and tr.proof_evidence.get("result") is not None:
            calculate_result = tr.proof_evidence["result"]
            break
    if calculate_result is not None:
        percentage = round(float(calculate_result), 1)
        print(f"   Using calculate tool result: {percentage}%")
    else:
        print(f"   Calculate tool did not return a result; falling back to manual compute")
        percentage = round(completed / total * 100, 1)
        print(f"   Manual percentage: {percentage}%")
    # Regex parse disabled – we trust the calculate tool result or manual math
    _unused = result2.assistant_text

    # ---- STEP 3: Write summary ----
    prompt3 = PROMPT_STEP3.format(
        summary_path=SUMMARY_PATH,
        percentage=percentage,
    )
    print(f"\n📝 Step 3 – Prompt: {prompt3[:60]}...")
    result3 = agent.run_turn(prompt3)
    turn_results.append(result3)
    print(f"Agent: {result3.assistant_text[:200]}")

    # ---- Aggregate proof chain ----
    print("\n" + "=" * 60)
    print("Proof chain summary")
    print("=" * 60)
    all_success = True
    all_tool_calls = []
    all_tool_results = []
    all_proof_log = []
    for i, r in enumerate(turn_results, 1):
        print(f"\nTurn {i}:")
        if r.tool_calls:
            for tc in r.tool_calls:
                fn = tc.get("function", {})
                print(f"  → {fn.get('name')}({fn.get('arguments', '')})")
                all_tool_calls.append(tc)
            for tr in r.tool_results:
                status = "✅ VERIFIED" if tr.success else "❌ FAILED"
                print(f"    [{status}] {tr.proof_claim}")
                all_tool_results.append(tr)
                if not tr.success:
                    all_success = False
            for entry in r.proof_log:
                all_proof_log.append(entry)
        else:
            print("  (No tools used)")

    # ---- Final external verification ----
    print("\n" + "-" * 60)
    print("External verification of summary file:")
    summary_ok, summary_checks = verify_summary_file()
    for check, ok in summary_checks.items():
        print(f"  [{'✅' if ok else '❌'}] {check}")

    # ---- Display written summary ----
    if summary_ok:
        print("\n" + "=" * 60)
        print("Generated summary:")
        print("=" * 60)
        print(Path(SUMMARY_PATH).read_text(encoding="utf-8"))

    # ---- Save structured result ----
    out = Path("demo-task-manager-result.json")
    out.write_text(json.dumps({
        "timestamp": result3.timestamp,
        "model": config["model_id"],
        "turns": [
            {
                "prompt": r.user_input,
                "assistant_text": r.assistant_text,
                "tool_calls": r.tool_calls,
                "tool_results": [tr.to_dict() for tr in r.tool_results],
                "proof_log": r.proof_log,
            }
            for r in turn_results
        ],
        "parsed_counts": {"total": total, "completed": completed, "pending": pending, "percentage": percentage},
        "tools_success": all_success,
        "external_verification": summary_checks,
        "overall_success": all_success and summary_ok,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved full proof chain to {out}")

    # Exit code reflects overall success
    sys.exit(0 if (all_success and summary_ok) else 1)


if __name__ == "__main__":
    main()
