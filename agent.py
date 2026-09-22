#!/usr/bin/env python3
"""
agent.py – CLI entry point for the Proof-First Personal Agent.

Usage:
    python agent.py "Your prompt here"          # Single turn
    python agent.py                             # Interactive REPL
    python agent.py --system "Extra context"    # With extra system prompt
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core.config import config
from core.agent import Agent


def run_repl(agent: Agent, extra_system: str = None):
    print("Proof-First Personal Agent")
    print(f"Model: {config['model_id']}")
    print("Type 'exit' or press Ctrl+C to quit.\n")
    while True:
        try:
            user_input = input("You> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break
        if not user_input or user_input.lower() in ("exit", "quit"):
            print("Goodbye.")
            break
        result = agent.run_turn(user_input, extra_system=extra_system)
        print(f"\nAgent> {result.assistant_text}\n")
        if result.tool_calls:
            print("[Tools used]")
            for tc, tr in zip(result.tool_calls, result.tool_results):
                status = "OK" if tr.success else "FAIL"
                print(f"  [{status}] {tc['function']['name']}: {tr.proof_claim}")
            print()


def run_single(agent: Agent, prompt: str, extra_system: str = None):
    print(f"Model: {config['model_id']}")
    print(f"Prompt: {prompt}\n")
    result = agent.run_turn(prompt, extra_system=extra_system)
    print(f"Agent> {result.assistant_text}\n")
    if result.tool_calls:
        print("[Tool calls]")
        for tc in result.tool_calls:
            fn = tc.get("function", {})
            print(f"  - {fn.get('name')}({fn.get('arguments', '')})")
        print("\n[Proof log]")
        for entry in result.proof_log:
            print(f"  - {entry['tool']}: {entry['claim']}")
    # Save
    out = Path("agent-result.json")
    out.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    print(f"\nSaved result to {out}")


def main():
    parser = argparse.ArgumentParser(description="Proof-First Personal Agent")
    parser.add_argument("prompt", nargs="?", help="Single-turn prompt")
    parser.add_argument("--system", default=None, help="Extra system context")
    args = parser.parse_args()

    if not config["nebius_api_key"]:
        print("ERROR: NEBIUS_API_KEY not found.")
        print("Export it or put it in ~/.openclaw/secrets/nebius.env")
        sys.exit(1)

    agent = Agent()

    if args.prompt:
        run_single(agent, args.prompt, extra_system=args.system)
    else:
        run_repl(agent, extra_system=args.system)


if __name__ == "__main__":
    main()
