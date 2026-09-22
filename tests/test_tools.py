#!/usr/bin/env python3
"""
Unit tests for core.tools.
Run with: python tests/test_tools.py
"""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.tools import ToolExecutor, ToolResult


def test_tool_result_dict():
    r = ToolResult(success=True, content="ok", proof_claim="did it", proof_evidence={"x": 1})
    d = r.to_dict()
    assert d["result"] == "ok"
    assert d["proof"]["claim"] == "did it"
    print("[PASS] test_tool_result_dict")


def test_tool_result_error():
    r = ToolResult(success=False, error="boom")
    d = r.to_dict()
    assert d["error"] == "boom"
    print("[PASS] test_tool_result_error")


def test_executor_schemas():
    ex = ToolExecutor()
    schemas = ex.schemas()
    names = {s["function"]["name"] for s in schemas}
    assert "read_file" in names
    assert "write_file" in names
    assert "list_dir" in names
    assert "run_command" in names
    print(f"[PASS] test_executor_schemas: {names}")


def test_read_file_tool():
    ex = ToolExecutor()
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("test content")
        f.flush()
        path = f.name
    try:
        result = ex.execute({"function": {"name": "read_file", "arguments": json.dumps({"path": path})}})
        assert result.success
        assert result.content == "test content"
        print("[PASS] test_read_file_tool")
    finally:
        os.unlink(path)


def test_write_file_verifies():
    ex = ToolExecutor()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "out.txt")
        result = ex.execute({
            "function": {
                "name": "write_file",
                "arguments": json.dumps({"path": path, "text": "hello"}),
            }
        })
        assert result.success, result.error
        assert os.path.exists(path)
        assert Path(path).read_text() == "hello"
        print("[PASS] test_write_file_verifies")


def test_list_dir_tool():
    ex = ToolExecutor()
    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "a.txt").write_text("A")
        Path(tmpdir, "b").mkdir()
        result = ex.execute({
            "function": {
                "name": "list_dir",
                "arguments": json.dumps({"path": tmpdir}),
            }
        })
        assert result.success
        items = result.content
        assert isinstance(items, list)
        assert len(items) == 2
        print("[PASS] test_list_dir_tool")


def test_run_command_tool():
    ex = ToolExecutor()
    result = ex.execute({
        "function": {
            "name": "run_command",
            "arguments": json.dumps({"command": "echo hello_agent"}),
        }
    })
    assert result.success
    assert "hello_agent" in result.content["stdout"]
    print("[PASS] test_run_command_tool")


def test_unknown_tool():
    ex = ToolExecutor()
    result = ex.execute({"function": {"name": "nonexistent", "arguments": "{}"}})
    assert not result.success
    assert "Unknown tool" in result.error
    print("[PASS] test_unknown_tool")


def test_bad_arguments():
    ex = ToolExecutor()
    result = ex.execute({
        "function": {
            "name": "write_file",
            "arguments": json.dumps({"path": "/tmp/x.txt"}),  # missing "text"
        }
    })
    assert not result.success
    assert "Bad arguments" in result.error or "missing" in result.error.lower()
    print("[PASS] test_bad_arguments")


def test_execute_all_batch():
    ex = ToolExecutor()
    results = ex.execute_all([
        {"function": {"name": "run_command", "arguments": json.dumps({"command": "echo one"})}},
        {"function": {"name": "run_command", "arguments": json.dumps({"command": "echo two"})}},
    ])
    assert len(results) == 2
    assert all(r.success for r in results)
    print("[PASS] test_execute_all_batch")


def run_all():
    tests = [
        test_tool_result_dict,
        test_tool_result_error,
        test_executor_schemas,
        test_read_file_tool,
        test_write_file_verifies,
        test_list_dir_tool,
        test_run_command_tool,
        test_unknown_tool,
        test_bad_arguments,
        test_execute_all_batch,
    ]
    passed = 0
    failed = 0
    print("=" * 60)
    print("Tools module tests")
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
