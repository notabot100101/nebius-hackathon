"""
File-based memory module for the Proof-First Personal Agent.
Uses atomic writes (temp file + rename) and timestamped JSON for persistence.
"""

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Optional, List, Dict, Any


class Memory:
    """Memory manager using plain file-based persistence."""

    def __init__(self, base_path: str):
        self.base = Path(base_path).resolve()
        self.short_term = self.base / "short_term"
        self.long_term = self.base / "long_term"
        self.state_dir = self.base / "state"

        for d in (self.short_term, self.long_term, self.state_dir):
            d.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Low-level file ops
    # ------------------------------------------------------------------ #
    def read(self, path: str) -> Optional[str]:
        """Read a text file relative to the memory base."""
        full_path = self._resolve(path)
        if not full_path.exists():
            return None
        try:
            return full_path.read_text(encoding="utf-8")
        except Exception:
            return None

    def write(self, path: str, content: str) -> bool:
        """Atomically write content to a memory file."""
        full_path = self._resolve(path)
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            fd, temp_path = tempfile.mkstemp(
                prefix=full_path.name + ".tmp.",
                suffix=".tmp",
                dir=full_path.parent,
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(content)
                os.replace(temp_path, full_path)
                return True
            except Exception:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return False
        except Exception:
            return False

    def list_paths(self, prefix: str = "") -> List[str]:
        """List all files under a prefix, returning paths relative to base."""
        base_dir = self.base / prefix if prefix else self.base
        if not base_dir.exists():
            return []
        try:
            paths = []
            for root, _dirs, files in os.walk(base_dir):
                for f in files:
                    fp = Path(root) / f
                    rel = str(fp.relative_to(self.base))
                    paths.append(rel)
            return sorted(paths)
        except Exception:
            return []

    # ------------------------------------------------------------------ #
    # State
    # ------------------------------------------------------------------ #
    def get_state(self) -> Dict[str, Any]:
        """Load the agent state JSON."""
        raw = self.read("state/state.json")
        if raw:
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                pass
        return {
            "version": "1.0",
            "facts_count": 0,
            "history_count": 0,
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def set_state(self, state: Dict[str, Any]) -> bool:
        """Persist the agent state JSON."""
        state["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            return self.write("state/state.json", json.dumps(state, indent=2))
        except Exception:
            return False

    # ------------------------------------------------------------------ #
    # Proof storage
    # ------------------------------------------------------------------ #
    def store_proof(self, claim: str, evidence: Dict[str, Any]) -> bool:
        """Store a verified claim + evidence atomically under long_term/facts/."""
        import hashlib

        claim_hash = hashlib.sha256(claim.encode()).hexdigest()[:16]
        fact_path = f"long_term/facts/{claim_hash}.json"
        proof = {
            "claim": claim,
            "evidence": evidence,
            "verified": True,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        return self.write(fact_path, json.dumps(proof, indent=2))

    def get_proof(self, claim: str) -> Optional[Dict[str, Any]]:
        """Find a proof by exact claim match in long_term/facts/."""
        facts_dir = self.long_term / "facts"
        if not facts_dir.exists():
            return None
        for p in facts_dir.iterdir():
            if p.suffix != ".json":
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if data.get("claim") == claim:
                    return data.get("evidence")
            except Exception:
                continue
        return None

    def list_proofs(self) -> List[Dict[str, Any]]:
        """Return all stored proofs."""
        results = []
        facts_dir = self.long_term / "facts"
        if not facts_dir.exists():
            return results
        for p in sorted(facts_dir.glob("*.json")):
            try:
                results.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                continue
        return results

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _resolve(self, path: str) -> Path:
        """Resolve a relative path against the memory base directory."""
        cleaned = Path(path).as_posix().lstrip("/")
        # Prevent path traversal out of base
        resolved = (self.base / cleaned).resolve()
        if not str(resolved).startswith(str(self.base)):
            raise ValueError(f"Path traversal blocked: {path}")
        return resolved


# Singleton helper
_default_memory: Optional[Memory] = None


def get_memory(base_path: Optional[str] = None) -> Memory:
    global _default_memory
    if _default_memory is None:
        path = base_path or str(Path.home() / ".nebius-hackathon" / "memory")
        _default_memory = Memory(path)
    return _default_memory
