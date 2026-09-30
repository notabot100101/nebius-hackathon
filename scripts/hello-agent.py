#!/usr/bin/env python3
"""
hello-agent.py – One full agent turn via Nebius API.

Usage:
    python scripts/hello-agent.py "List the files in /tmp"

This script runs a single agent turn:
  1. Sends your prompt to the Nemotron model via Nebius Token Factory.
  2. The model may decide to call tools (read_file, list_dir, etc.).
  3. Each tool call is executed locally and verified (trust-first).
  4. Results are sent back to the model for a final answer.
  5. A JSON summary is written to hello-agent-result.json.
"""

import json
import os
import sys
from pathlib import Path

# Ensure core/ is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import config
from core.agent import Agent


def main():
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hello! List the files in /tmp and tell me how many there are."

    if not config["nebius_api_key"]:
        print("ERROR: NEBIUS_API_KEY not found.")
        print("Export it or put it in ~/.openclaw/secrets/nebius.env")
        sys.exit(1)

    print(f"Model: {config['model_id']}")
    print(f"Prompt: {user_input}")
    print("-" * 60)

    agent = Agent()
    result = agent.run_turn(user_input)

    print(f"\nAssistant:\n{result.assistant_text}\n")

    if result.tool_calls:
        print("Tool calls made:")
        for tc in result.tool_calls:
            fn = tc.get("function", {})
            print(f"  - {fn.get('name')}({fn.get('arguments', '')})")
        print("\nTool results:")
        for tr in result.tool_results:
            status = "OK" if tr.success else "FAIL"
            print(f"  [{status}] {tr.proof_claim}")
    else:
        print("(No tool calls were used for this turn.)")

    print("\nProof log:")
    for entry in result.proof_log:
        print(f"  - {entry['tool']}: {entry['claim']}")

    # Save summary
    summary_path = Path("hello-agent-result.json")
    summary_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    print(f"\nSaved summary to {summary_path}")

    sys.exit(0)


if __name__ == "__main__":
    main()
