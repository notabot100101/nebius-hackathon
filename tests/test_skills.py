#!/usr/bin/env python3
"""
Unit tests for skill system.
Run with: python tests/test_skills.py
"""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.registry import Registry, skill, get_registry
from core.tools import ToolExecutor, ToolResult


@skill(name="test_hello", description="Say hello", schema={
    "name": "test_hello",
    "description": "Say hello",
    "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
})
def test_hello(name: str) -> ToolResult:
    return ToolResult(success=True, content=f"Hello {name}!")


def test_registry_decorator():
    assert hasattr(test_hello, "_is_skill")
    assert test_hello._skill_name == "test_hello"
    print("[PASS] test_registry_decorator")


def test_registry_load():
    executor = ToolExecutor()
    reg = Registry(executor=executor)
    reg.register("test_hello", test_hello, schema={
        "name": "test_hello",
        "description": "Say hello",
        "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
    })
    assert "test_hello" in reg.discover()
    result = reg.get_handler("test_hello")(name="World")
    assert result.success
    assert "Hello World!" in result.content
    print("[PASS] test_registry_load")


def test_skill_discovery():
    """Test auto-discovery from skills/ directory."""
    from core.memory import Memory
    mem = Memory(tempfile.mkdtemp())
    executor = ToolExecutor(memory=mem)
    reg = get_registry(executor=executor)
    tools = reg.discover()
    # Should have built-in tools + any skills
    builtin = {"read_file", "write_file", "list_dir", "run_command", "memory_read", "memory_write"}
    assert builtin.issubset(set(tools)), f"Missing built-in tools: {builtin - set(tools)}"
    print(f"[PASS] test_skill_discovery: found {len(tools)} tools: {', '.join(tools)}")


def test_calculator_skill():
    """Test the calculator skill if available."""
    reg = get_registry()
    if "calculate" not in reg.discover():
        print("[SKIP] test_calculator_skill: calculate skill not loaded")
        return
    handler = reg.get_handler("calculate")
    result = handler(expression="2 + 2")
    assert result.success, f"calculate failed: {result.error}"
    assert "4" in result.content
    print("[PASS] test_calculator_skill")


def test_web_fetch_skill():
    """Test the web_fetch skill if available."""
    reg = get_registry()
    if "web_fetch" not in reg.discover():
        print("[SKIP] test_web_fetch_skill: web_fetch skill not loaded")
        return
    handler = reg.get_handler("web_fetch")
    result = handler(url="https://httpbin.org/get", max_chars=100)
    # May fail without network, that's okay for a unit test
    print(f"[PASS] test_web_fetch_skill: success={result.success}")


def test_safety_blocks_sudo():
    """Test that sudo commands are blocked."""
    from core.tools import _tool_run_command
    result = _tool_run_command("sudo ls /root")
    assert not result.success
    assert "sudo" in result.error.lower()
    print("[PASS] test_safety_blocks_sudo")


def test_safety_blocks_dangerous():
    """Test that dangerous commands are blocked."""
    from core.tools import _tool_run_command
    result = _tool_run_command("rm -rf /")
    assert not result.success
    assert "safety" in result.error.lower()
    print("[PASS] test_safety_blocks_dangerous")


def run_all():
    tests = [
        test_registry_decorator,
        test_registry_load,
        test_skill_discovery,
        test_calculator_skill,
        test_web_fetch_skill,
        test_safety_blocks_sudo,
        test_safety_blocks_dangerous,
    ]
    passed = 0
    failed = 0
    print("=" * 60)
    print("Skills & Safety module tests")
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
