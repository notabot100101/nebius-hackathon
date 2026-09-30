"""
Tool executor for the Trust-First Personal Agent.
Executes tool calls from the model and verifies results.
"""

import json
import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Callable, List, Optional


class ToolResult:
    """Result of a tool execution with proof evidence."""

    def __init__(
        self,
        success: bool,
        content: Any = None,
        error: str = None,
        proof_claim: str = None,
        proof_evidence: Dict[str, Any] = None,
    ):
        self.success = success
        self.content = content
        self.error = error
        self.proof_claim = proof_claim or "tool executed"
        self.proof_evidence = proof_evidence or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict suitable for returning to the model."""
        if self.error:
            return {
                "error": self.error,
                "proof": {"claim": self.proof_claim, "evidence": self.proof_evidence},
            }
        return {
            "result": self.content if self.content is not None else "ok",
            "proof": {"claim": self.proof_claim, "evidence": self.proof_evidence},
        }

    def __repr__(self) -> str:
        return f"ToolResult(success={self.success}, content={self.content!r}, error={self.error!r})"


# ------------------------------------------------------------------ #
# Built-in tool implementations
# ------------------------------------------------------------------ #

def _tool_read_file(path: str) -> ToolResult:
    full = Path(path).expanduser()
    if not full.exists():
        return ToolResult(success=False, error=f"File not found: {path}")
    try:
        text = full.read_text(encoding="utf-8", errors="replace")
        return ToolResult(
            success=True,
            content=text[:4000],  # Truncate for context window safety
            proof_claim=f"read_file succeeded for {path}",
            proof_evidence={"path": str(full), "bytes_read": len(text)},
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


def _tool_write_file(path: str, text: str) -> ToolResult:
    full = Path(path).expanduser()
    try:
        full.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(
            prefix=full.name + ".tmp.", suffix=".tmp", dir=full.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(text)
            os.replace(tmp, full)
        except Exception:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

        # Proof: read back and verify
        written = full.read_text(encoding="utf-8")
        verified = written == text
        return ToolResult(
            success=verified,
            content=f"Wrote {len(text)} bytes to {path}",
            error=None if verified else "Verification failed: content mismatch after write",
            proof_claim=f"write_file {'verified' if verified else 'FAILED verification'} for {path}",
            proof_evidence={
                "path": str(full),
                "expected_bytes": len(text),
                "actual_bytes": len(written),
                "match": verified,
            },
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


def _tool_list_dir(path: str = ".") -> ToolResult:
    full = Path(path).expanduser()
    if not full.exists():
        return ToolResult(success=False, error=f"Path not found: {path}")
    try:
        items = []
        for item in sorted(full.iterdir(), key=lambda x: x.name):
            st = item.stat()
            items.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size": st.st_size,
                "modified": st.st_mtime,
            })
        return ToolResult(
            success=True,
            content=items,
            proof_claim=f"list_dir succeeded for {path}",
            proof_evidence={"path": str(full), "count": len(items)},
        )
    except Exception as e:
        return ToolResult(success=False, error=str(e))


def _tool_run_command(command: str) -> ToolResult:
    # Safety gate: reject known dangerous patterns
    dangerous = ["rm -rf /", ":(){ :|:& };:", "> /dev/sda", "mkfs.", "dd if=/dev/zero"]
    for bad in dangerous:
        if bad in command.lower():
            return ToolResult(success=False, error=f"Command rejected for safety: contains '{bad}'")
    
    # Reject sudo escalation
    if command.strip().startswith("sudo "):
        return ToolResult(success=False, error="Command rejected: sudo not allowed")
    
    try:
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(Path.home()),
        )
        return ToolResult(
            success=result.returncode == 0,
            content={
                "stdout": result.stdout[:4000] if result.stdout else "",
                "stderr": result.stderr[:2000] if result.stderr else "",
                "returncode": result.returncode,
            },
            error=None if result.returncode == 0 else f"Exit code {result.returncode}",
            proof_claim=f"run_command finished: {command}",
            proof_evidence={
                "command": command,
                "returncode": result.returncode,
                "stdout_bytes": len(result.stdout) if result.stdout else 0,
            },
        )
    except subprocess.TimeoutExpired:
        return ToolResult(success=False, error="Command timed out after 30s")
    except FileNotFoundError as e:
        return ToolResult(success=False, error=f"Command not found: {e}")
    except Exception as e:
        return ToolResult(success=False, error=str(e))


def _tool_memory_read(path: str, memory) -> ToolResult:
    content = memory.read(path)
    if content is None:
        return ToolResult(
            success=True,
            content="(empty – no file at this path yet)",
            proof_claim=f"memory_read returned empty for {path}",
            proof_evidence={"path": path},
        )
    return ToolResult(
        success=True,
        content=content[:4000],
        proof_claim=f"memory_read succeeded for {path}",
        proof_evidence={"path": path, "bytes": len(content)},
    )


def _tool_memory_write(path: str, content: str, memory) -> ToolResult:
    ok = memory.write(path, content)
    if ok:
        # Verify read-back
        back = memory.read(path)
        verified = back == content
        return ToolResult(
            success=verified,
            content=f"Memory write {'verified' if verified else 'failed verification'} for {path}",
            proof_claim=f"memory_write {'verified' if verified else 'FAILED'} for {path}",
            proof_evidence={"path": path, "match": verified},
        )
    return ToolResult(success=False, error=f"Failed to write memory at {path}")


# ------------------------------------------------------------------ #
# Tool schemas for the LLM (OpenAI function-calling format)
# ------------------------------------------------------------------ #

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a text file from disk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative file path"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text to a file atomically. Verifies by reading back.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "text": {"type": "string", "description": "Full content to write"},
                },
                "required": ["path", "text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and directories at a path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path (default: current directory)",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a safe shell command and capture stdout/stderr.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command string"},
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "memory_read",
            "description": "Read content from the agent's memory store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Memory file path relative to memory base"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "memory_write",
            "description": "Write content to the agent's memory store atomically.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Memory file path"},
                    "content": {"type": "string", "description": "Text content to store"},
                },
                "required": ["path", "content"],
            },
        },
    },
]


# ------------------------------------------------------------------ #
# ToolExecutor
# ------------------------------------------------------------------ #

class ToolExecutor:
    """Dispatches tool calls to the right implementation."""

    def __init__(self, memory=None):
        self.memory = memory
        self._handlers: Dict[str, Callable] = {
            "read_file": _tool_read_file,
            "write_file": _tool_write_file,
            "list_dir": _tool_list_dir,
            "run_command": _tool_run_command,
        }
        if memory is not None:
            self._handlers["memory_read"] = lambda **kw: _tool_memory_read(memory=memory, **kw)
            self._handlers["memory_write"] = lambda **kw: _tool_memory_write(memory=memory, **kw)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def schemas(self) -> List[Dict[str, Any]]:
        """Return OpenAI-compatible tool schemas."""
        base = list(TOOL_SCHEMAS)
        if self.memory is not None:
            return base  # Already includes memory tools
        # Strip memory tools if no memory attached
        return [s for s in base if s["function"]["name"] not in ("memory_read", "memory_write")]

    def execute(self, tool_call: Dict[str, Any]) -> ToolResult:
        """
        Execute a single tool call from the LLM.
        tool_call format: {"id": "...", "function": {"name": "...", "arguments": "..."}}
        """
        func = tool_call.get("function", tool_call)
        name = func.get("name")
        raw_args = func.get("arguments", "{}")

        handler = self._handlers.get(name)
        if handler is None:
            return ToolResult(success=False, error=f"Unknown tool: {name}")

        try:
            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        except json.JSONDecodeError:
            return ToolResult(success=False, error=f"Invalid JSON arguments for {name}: {raw_args!r}")

        try:
            return handler(**args)
        except TypeError as e:
            return ToolResult(success=False, error=f"Bad arguments for {name}: {e}")
        except Exception as e:
            return ToolResult(success=False, error=f"Exception in {name}: {e}")

    def execute_all(self, tool_calls: List[Dict[str, Any]]) -> List[ToolResult]:
        """Execute a batch of tool calls."""
        return [self.execute(tc) for tc in tool_calls]

    def register(self, name: str, handler: Callable, schema: Dict[str, Any] = None):
        """Dynamically register a new tool."""
        self._handlers[name] = handler
        if schema is not None:
            schema["type"] = "function"
            if "function" not in schema:
                schema = {"type": "function", "function": schema}
            # Replace existing schema or append
            for i, s in enumerate(TOOL_SCHEMAS):
                if s["function"]["name"] == name:
                    TOOL_SCHEMAS[i] = schema
                    return
            TOOL_SCHEMAS.append(schema)
