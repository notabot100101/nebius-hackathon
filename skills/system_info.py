"""
system_info skill – Trust-First Personal Agent.

Reports lightweight system health: disk usage, memory, load,
and project-specific status (git state, credit balance hint).
Uses only stdlib to stay dependency-free.
"""

import os
import shutil
import time
from pathlib import Path
from typing import Optional

from core.registry import skill
from core.tools import ToolResult


def _get_disk_info(path: str = ".") -> dict:
    try:
        usage = shutil.disk_usage(path)
        total_gb = usage.total / (1024 ** 3)
        free_gb = usage.free / (1024 ** 3)
        used_pct = round((usage.used / usage.total) * 100, 1)
        return {
            "path": path,
            "total_gb": round(total_gb, 2),
            "free_gb": round(free_gb, 2),
            "used_percent": used_pct,
        }
    except Exception as e:
        return {"error": str(e)}


def _get_load_info() -> dict:
    try:
        load1, load5, load15 = os.getloadavg()
        cpu_count = os.cpu_count() or 1
        return {
            "load1": round(load1, 2),
            "load5": round(load5, 2),
            "load15": round(load15, 2),
            "cpus": cpu_count,
            "load1_per_cpu": round(load1 / cpu_count, 2),
        }
    except Exception as e:
        return {"error": str(e)}


def _get_mem_info() -> Optional[dict]:
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.read().splitlines()
        mem_data = {}
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                mem_data[key.strip()] = val.strip().split()[0]
        total_kb = int(mem_data.get("MemTotal", 0))
        free_kb = int(mem_data.get("MemFree", 0))
        avail_kb = int(mem_data.get("MemAvailable", free_kb))
        total_gb = total_kb / (1024 ** 2)
        avail_gb = avail_kb / (1024 ** 2)
        used_pct = round(((total_kb - avail_kb) / total_kb) * 100, 1) if total_kb else 0
        return {
            "total_gb": round(total_gb, 2),
            "available_gb": round(avail_gb, 2),
            "used_percent": used_pct,
        }
    except Exception as e:
        return {"error": str(e)}


def _get_project_git_info(project_path: str = ".") -> dict:
    """Git status summary for a project directory."""
    from subprocess import run, PIPE
    p = Path(project_path).expanduser().resolve()
    if not (p / ".git").exists():
        return {"is_git_repo": False}
    try:
        commit = run(["git", "-C", str(p), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=10)
        branch = run(["git", "-C", str(p), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, timeout=10)
        dirty = run(["git", "-C", str(p), "status", "--porcelain"], capture_output=True, text=True, timeout=10)
        return {
            "is_git_repo": True,
            "commit": commit.stdout.strip() if commit.returncode == 0 else None,
            "branch": branch.stdout.strip() if branch.returncode == 0 else None,
            "dirty": bool(dirty.stdout.strip()),
        }
    except Exception as e:
        return {"error": str(e)}


@skill(
    name="system_info",
    description="Report system health and project git status.",
    schema={
        "name": "system_info",
        "description": "Report lightweight system health: disk usage, memory, load average, and optional git status for a project path.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Optional project directory to check git status for (default: current directory)",
                },
            },
        },
    },
)
def system_info(project_path: str = ".") -> ToolResult:
    """Collect system metrics and optional git info."""
    result = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "disk": _get_disk_info("."),
        "memory": _get_mem_info() or {"error": "unable to read memory info"},
        "load": _get_load_info(),
        "git": _get_project_git_info(project_path),
    }

    # Human-readable summary
    lines = [
        f"System health at {result['timestamp']}",
        f"  Disk: {result['disk'].get('free_gb', '?')} GB free / {result['disk'].get('total_gb', '?')} GB total ({result['disk'].get('used_percent', '?')}% used)",
        f"  Memory: {result['memory'].get('available_gb', '?')} GB available / {result['memory'].get('total_gb', '?')} GB total ({result['memory'].get('used_percent', '?')}% used)",
        f"  Load (1m): {result['load'].get('load1', '?')} on {result['load'].get('cpus', '?')} CPUs",
    ]
    if result["git"].get("is_git_repo"):
        git = result["git"]
        lines.append(f"  Git: {git.get('branch', '?')} @ {git.get('commit', '?')}{' (dirty)' if git.get('dirty') else ''}")
    elif "error" not in result["git"]:
        lines.append("  Git: not a git repository")

    summary = "\n".join(lines)
    return ToolResult(
        success=True,
        content=summary,
        proof_claim="system_info collected health metrics",
        proof_evidence=result,
    )
