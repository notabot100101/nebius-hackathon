"""
Core module for Trust-First Personal Agent.

Exports:
  - config: dict with API key, model, paths
  - Memory: file-based persistence
  - ToolExecutor: dispatches tool calls and verifies results
  - Registry: skill discovery and registration
  - NebiusClient: minimal OpenAI-compatible API client (stdlib only)
  - Agent: single-turn agent loop

Design constraints:
  - Standard library + requests (we use urllib.request to stay dependency-free)
  - Synchronous only
  - Every action checked and proved
"""

from core.config import config, load_config
from core.memory import Memory, get_memory
from core.tools import ToolExecutor, ToolResult, TOOL_SCHEMAS
from core.registry import Registry, skill, get_registry

__all__ = [
    "config",
    "load_config",
    "Memory",
    "get_memory",
    "ToolExecutor",
    "ToolResult",
    "TOOL_SCHEMAS",
    "Registry",
    "skill",
    "get_registry",
]
