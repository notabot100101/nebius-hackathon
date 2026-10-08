#!/usr/bin/env python3
"""
Unit tests for core.agent response parsing helpers.
Run with: python tests/test_agent.py
"""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.agent import Agent, NebiusClient


def test_extract_content_string():
    response = {"choices": [{"message": {"content": "NEMOTRON-OK"}}]}
    assert NebiusClient.extract_content(response) == "NEMOTRON-OK"
    print("[PASS] test_extract_content_string")


def test_extract_content_parts():
    response = {
        "choices": [
            {"message": {"content": [{"type": "text", "text": "NEMOTRON"}, {"type": "text", "text": "-OK"}]}}
        ]
    }
    assert NebiusClient.extract_content(response) == "NEMOTRON-OK"
    print("[PASS] test_extract_content_parts")


def test_extract_content_none_acknowledged():
    response = {"choices": [{"message": {"content": None}}]}
    assert NebiusClient.extract_content(response) == "(acknowledged)"
    print("[PASS] test_extract_content_none_acknowledged")


def test_agent_loops_until_final_answer():
    class FakeClient:
        def __init__(self, path):
            self.path = path
            self.calls = 0

        def chat(self, messages, tools=None, max_tokens=512, temperature=0.3, max_retries=None):
            self.calls += 1
            responses = [
                {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [{
                    "id": "call-read",
                    "type": "function",
                    "function": {"name": "read_file", "arguments": json.dumps({"path": self.path})},
                }]}}]},
                {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [{
                    "id": "call-write",
                    "type": "function",
                    "function": {"name": "write_file", "arguments": json.dumps({"path": self.path, "text": "verified"})},
                }]}}]},
                {"choices": [{"message": {"role": "assistant", "content": "Done and verified."}}]},
            ]
            return responses[self.calls - 1]

        extract_message = staticmethod(NebiusClient.extract_message)
        extract_tool_calls = staticmethod(NebiusClient.extract_tool_calls)
        content_to_text = staticmethod(NebiusClient.content_to_text)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = str(Path(tmpdir) / "demo.txt")
        Path(path).write_text("draft", encoding="utf-8")
        agent = Agent(api_key="test", memory_dir=str(Path(tmpdir) / "memory"))
        agent.client = FakeClient(path)
        result = agent.run_turn("Read then update the file")
        assert result.assistant_text == "Done and verified."
        assert len(result.tool_calls) == 2
        assert [c["function"]["name"] for c in result.tool_calls] == ["read_file", "write_file"]
        assert Path(path).read_text(encoding="utf-8") == "verified"
        print("[PASS] test_agent_loops_until_final_answer")


def run_all():
    tests = [
        test_extract_content_string,
        test_extract_content_parts,
        test_extract_content_none_acknowledged,
        test_agent_loops_until_final_answer,
    ]
    passed = 0
    failed = 0
    print("=" * 60)
    print("Agent module tests")
    print("=" * 60)
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {t.__name__}: {e}")
            failed += 1
    print("=" * 60)
    print(f"Result: {passed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
