"""
web_search skill – Proof-First Personal Agent.

A minimal skill that fetches a URL and returns the text content.
Uses only stdlib (urllib) to stay dependency-free.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any

from core.registry import skill
from core.tools import ToolResult


@skill(
    name="web_fetch",
    description="Fetch a web page and return its text content.",
    schema={
        "name": "web_fetch",
        "description": "Fetch a web page and return its text content.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch"},
                "max_chars": {"type": "integer", "description": "Maximum characters to return (default 4000)"},
            },
            "required": ["url"],
        },
    },
)
def web_fetch(url: str, max_chars: int = 4000) -> ToolResult:
    """Fetch a URL and return text content."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ProofFirstAgent/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8", errors="replace")[:max_chars]
            return ToolResult(
                success=True,
                content=content,
                proof_claim=f"web_fetch succeeded for {url}",
                proof_evidence={"url": url, "status": resp.status, "bytes": len(content)},
            )
    except urllib.error.HTTPError as e:
        return ToolResult(
            success=False,
            error=f"HTTP {e.code}: {e.reason}",
            proof_claim=f"web_fetch failed for {url}",
            proof_evidence={"url": url, "status": e.code},
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=str(e),
            proof_claim=f"web_fetch failed for {url}",
            proof_evidence={"url": url, "error": str(e)},
        )
