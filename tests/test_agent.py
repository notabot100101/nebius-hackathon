#!/usr/bin/env python3
"""
Unit tests for core.agent response parsing helpers.
Run with: python tests/test_agent.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.agent import NebiusClient


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


def run_all():
    tests = [
        test_extract_content_string,
        test_extract_content_parts,
        test_extract_content_none_acknowledged,
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
