#!/usr/bin/env python3
"""
Unit tests for core.memory.
Run with: python tests/test_memory.py
"""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.memory import Memory


def test_read_write():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = Memory(tmpdir)
        assert mem.write("notes/test.txt", "hello world")
        assert mem.read("notes/test.txt") == "hello world"
        print("[PASS] test_read_write")


def test_atomic_overwrite():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = Memory(tmpdir)
        mem.write("file.txt", "v1")
        mem.write("file.txt", "v2")
        assert mem.read("file.txt") == "v2"
        print("[PASS] test_atomic_overwrite")


def test_read_missing():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = Memory(tmpdir)
        assert mem.read("missing.txt") is None
        print("[PASS] test_read_missing")


def test_list_paths():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = Memory(tmpdir)
        mem.write("short_term/a.md", "A")
        mem.write("short_term/b.md", "B")
        mem.write("long_term/facts/x.json", '{"claim":"x"}')
        paths = mem.list_paths()
        assert len(paths) == 3
        assert all(p in paths for p in ["short_term/a.md", "short_term/b.md", "long_term/facts/x.json"])
        print("[PASS] test_list_paths")


def test_state_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = Memory(tmpdir)
        state = mem.get_state()
        assert state["version"] == "1.0"
        state["custom"] = 42
        assert mem.set_state(state)
        state2 = mem.get_state()
        assert state2["custom"] == 42
        print("[PASS] test_state_roundtrip")


def test_proof_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = Memory(tmpdir)
        claim = "the sky is blue"
        evidence = {"source": "observation", "time": "noon"}
        assert mem.store_proof(claim, evidence)
        retrieved = mem.get_proof(claim)
        assert retrieved == evidence
        assert len(mem.list_proofs()) == 1
        print("[PASS] test_proof_storage")


def test_path_traversal_blocked():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem = Memory(tmpdir)
        try:
            mem.write("../../../etc/passwd", "nope")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        print("[PASS] test_path_traversal_blocked")


def run_all():
    tests = [
        test_read_write,
        test_atomic_overwrite,
        test_read_missing,
        test_list_paths,
        test_state_roundtrip,
        test_proof_storage,
        test_path_traversal_blocked,
    ]
    passed = 0
    failed = 0
    print("=" * 60)
    print("Memory module tests")
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
