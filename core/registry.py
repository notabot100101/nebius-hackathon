"""
Skill registry for the Proof-First Personal Agent.
Discovers and registers skill modules from the skills/ directory.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Callable, Any

from core.tools import ToolExecutor


class Registry:
    """Registry that wraps a ToolExecutor and adds skill discovery."""

    def __init__(self, executor: ToolExecutor = None, skills_dir: str = None):
        self.executor = executor or ToolExecutor()
        self.skills_dir = Path(skills_dir) if skills_dir else Path(__file__).parent.parent / "skills"
        self._meta: Dict[str, Dict[str, Any]] = {}

    def discover(self) -> List[str]:
        """Return all available tool names."""
        return list(self.executor._handlers.keys())

    def describe(self, name: str) -> str:
        """Return a short description for a tool."""
        for schema in self.executor.schemas():
            if schema["function"]["name"] == name:
                return schema["function"].get("description", "")
        return self._meta.get(name, {}).get("description", "")

    def get_handler(self, name: str) -> Callable:
        """Get the handler callable for a tool."""
        if name not in self.executor._handlers:
            raise KeyError(f"Tool '{name}' not registered. Available: {self.discover()}")
        return self.executor._handlers[name]

    def register(self, name: str, handler: Callable, description: str = None, schema: Dict[str, Any] = None):
        """Register a skill (function) with optional OpenAI schema."""
        self.executor.register(name, handler, schema=schema)
        self._meta[name] = {"description": description or handler.__doc__ or ""}

    def load_skills_from_directory(self, directory: str = None):
        """Discover and load .py skill modules from a directory."""
        d = Path(directory) if directory else self.skills_dir
        if not d.exists():
            return
        for f in sorted(d.glob("*.py")):
            if f.name.startswith("_"):
                continue
            self._load_module(f)

    def _load_module(self, path: Path):
        """Load a single Python skill module and register decorated functions."""
        name = path.stem
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            if spec is None or spec.loader is None:
                return
            mod = importlib.util.module_from_spec(spec)
            # Keep sys.modules clean but allow imports within skill
            sys.modules[f"_agent_skill_{name}"] = mod
            spec.loader.exec_module(mod)
            for attr_name in dir(mod):
                obj = getattr(mod, attr_name)
                if callable(obj) and getattr(obj, "_is_skill", False):
                    self.register(
                        getattr(obj, "_skill_name", attr_name),
                        obj,
                        description=getattr(obj, "_skill_description", None),
                        schema=getattr(obj, "_skill_schema", None),
                    )
        except Exception as exc:
            print(f"[registry] Failed to load skill '{path}': {exc}")


# Decorator helpers
def skill(name: str = None, description: str = None, schema: Dict[str, Any] = None):
    """Decorator to mark a function as a registerable skill."""

    def decorator(func: Callable):
        func._is_skill = True
        func._skill_name = name or func.__name__
        func._skill_description = description or func.__doc__ or ""
        func._skill_schema = schema
        return func

    return decorator


def get_registry(executor: ToolExecutor = None, skills_dir: str = None) -> Registry:
    """Create a registry, load skills/, and return it."""
    reg = Registry(executor=executor, skills_dir=skills_dir)
    reg.load_skills_from_directory()
    return reg
