"""
Agent single-turn loop and Nebius API client.
Uses only urllib.request (stdlib) for HTTP.
"""

import json
import time
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional

from core.config import config
from core.memory import Memory
from core.tools import ToolExecutor, ToolResult
from core.registry import get_registry


# Retry constants (seconds)
_RETRY_BACKOFF_BASE = 1.5
_RETRY_MAX_DELAY = 30
_RETRY_STATUS_CODES = {429, 502, 503, 504}


SYSTEM_PROMPT = """You are a Trust-First Personal Agent. Every claim you make must be backed by evidence.
When you need to interact with the world, use the available tools.
After using a tool, verify the outcome before telling the user it succeeded.
Prefer facts over speculation. If you are unsure, say so."""


class NebiusClient:
    """Minimal OpenAI-compatible client for Nebius Token Factory."""

    def __init__(self, api_key: str, model: str, base_url: str, timeout: int = 60):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _should_retry(self, exc: Optional[Exception]) -> bool:
        """Determine whether an exception warrants a retry."""
        if exc is None:
            return False
        if isinstance(exc, urllib.error.HTTPError):
            return exc.code in _RETRY_STATUS_CODES
        # Treat transient network errors as retryable
        return isinstance(exc, (urllib.error.URLError, TimeoutError))

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        max_tokens: int = 512,
        temperature: float = 0.3,
        max_retries: int = None,
    ) -> Dict[str, Any]:
        """Chat completion with automatic retry on transient errors."""
        if max_retries is None:
            max_retries = config.get("max_retries", 3)

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools

        url = f"{self.base_url}/chat/completions"
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(max_retries + 1):
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            exc = None
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return json.loads(resp.read())
            except urllib.error.HTTPError as e:
                exc = e
                body = e.read().decode(errors="replace")[:800]
                if not self._should_retry(e):
                    return {"error": f"HTTP {e.code}: {body}"}
                # Retryable – continue to backoff below
            except Exception as e:
                exc = e
                if not self._should_retry(e):
                    return {"error": str(e)}
                # Retryable – continue to backoff below

            if attempt < max_retries:
                delay = min(_RETRY_BACKOFF_BASE * (2 ** attempt), _RETRY_MAX_DELAY)
                time.sleep(delay)
            else:
                # Exceeded retries
                if isinstance(exc, urllib.error.HTTPError):
                    body = exc.read().decode(errors="replace")[:800]
                    return {"error": f"HTTP {exc.code} after {max_retries + 1} attempts: {body}"}
                return {"error": f"{exc} after {max_retries + 1} attempts"}
        # Unreachable, but keeps type checker happy
        return {"error": "unexpected end of retry loop"}

    @staticmethod
    def extract_message(response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the assistant message dict from an API response."""
        if "error" in response:
            return {"role": "assistant", "content": f"API error: {response['error']}"}
        choices = response.get("choices", [])
        if not choices:
            return {"role": "assistant", "content": "(no response from model)"}
        return choices[0].get("message", {})

    @staticmethod
    def content_to_text(content: Any) -> str:
        """Normalize OpenAI-compatible message content into plain text.

        Some providers return message.content as a string; others may return a
        list of typed content parts. The agent only needs the text portion for
        summaries and health checks.
        """
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict):
                    text = part.get("text") or part.get("content")
                    if isinstance(text, str):
                        parts.append(text)
                    elif text is not None:
                        parts.append(str(text))
            return "".join(parts)
        return str(content)

    @staticmethod
    def extract_content(response: Dict[str, Any]) -> str:
        """Get plain text content from a response."""
        msg = NebiusClient.extract_message(response)
        content = msg.get("content")
        if content is None:
            return "(acknowledged)"
        text = NebiusClient.content_to_text(content)
        return text if text else "(empty)"

    @staticmethod
    def extract_tool_calls(response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get tool_calls list from a response."""
        msg = NebiusClient.extract_message(response)
        return msg.get("tool_calls", [])


class AgentTurnResult:
    """Result of a single agent turn."""

    def __init__(
        self,
        user_input: str,
        assistant_text: str,
        tool_calls: List[Dict[str, Any]],
        tool_results: List[ToolResult],
        proof_log: List[Dict[str, Any]],
        raw_messages: List[Dict[str, Any]],
    ):
        self.user_input = user_input
        self.assistant_text = assistant_text
        self.tool_calls = tool_calls
        self.tool_results = tool_results
        self.proof_log = proof_log
        self.raw_messages = raw_messages
        self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "user_input": self.user_input,
            "assistant_text": self.assistant_text,
            "tool_calls": self.tool_calls,
            "tool_results": [r.to_dict() for r in self.tool_results],
            "proof_log": self.proof_log,
        }


class Agent:
    """Multi-turn agent: maintains conversation history across turns."""

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        base_url: str = None,
        memory_dir: str = None,
        timeout: int = 60,
        skills_dir: str = None,
    ):
        cfg = config
        self.client = NebiusClient(
            api_key=api_key or cfg["nebius_api_key"],
            model=model or cfg["model_id"],
            base_url=base_url or cfg["base_url"],
            timeout=timeout or cfg["timeout"],
        )
        self.memory = Memory(memory_dir or cfg["memory_dir"])
        self.tools = ToolExecutor(memory=self.memory)
        self.history: List[Dict[str, Any]] = []
        self.turn_count = 0

        # Auto-discover skills from skills/ directory
        self.registry = get_registry(executor=self.tools, skills_dir=skills_dir)
        loaded = self.registry.discover()
        builtin = {"read_file", "write_file", "list_dir", "run_command", "memory_read", "memory_write"}
        skill_tools = [t for t in loaded if t not in builtin]
        if skill_tools:
            print(f"[Agent] Loaded skills: {', '.join(skill_tools)}")

    def reset_history(self):
        """Clear conversation history."""
        self.history = []
        self.turn_count = 0

    def run_turn(self, user_input: str, extra_system: str = None, max_tool_rounds: int = 8) -> AgentTurnResult:
        """Run one complete agent turn with persistent history."""
        self.turn_count += 1

        # Build messages: system + history + current user input
        system = SYSTEM_PROMPT
        if extra_system:
            system += "\n" + extra_system

        messages: List[Dict[str, Any]] = [{"role": "system", "content": system}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_input})

        # Initial model call
        response = self.client.chat(
            messages=messages,
            tools=self.tools.schemas(),
            max_tokens=512,
        )

        msg = self.client.extract_message(response)
        tool_calls = self.client.extract_tool_calls(response)
        all_tool_calls: List[Dict[str, Any]] = []
        proof_log: List[Dict[str, Any]] = []
        tool_results: List[ToolResult] = []

        rounds = 0
        while tool_calls and rounds < max_tool_rounds:
            rounds += 1
            all_tool_calls.extend(tool_calls)
            # Append assistant message with tool_calls
            messages.append(msg)

            for tc in tool_calls:
                result = self.tools.execute(tc)
                tool_results.append(result)
                proof_log.append({
                    "tool": tc.get("function", {}).get("name"),
                    "success": result.success,
                    "claim": result.proof_claim,
                    "evidence": result.proof_evidence,
                })

                # Store verified proofs in memory
                if result.success:
                    self.memory.store_proof(result.proof_claim, result.proof_evidence)

                # Append tool result message
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id"),
                    "name": tc.get("function", {}).get("name"),
                    "content": json.dumps(result.to_dict()),
                })

            # Continue the same turn. Some models emit one tool call at a time,
            # so keep looping until the model returns a final text answer.
            response = self.client.chat(
                messages=messages,
                tools=self.tools.schemas(),
                max_tokens=512,
            )
            msg = self.client.extract_message(response)
            tool_calls = self.client.extract_tool_calls(response)

        if tool_calls:
            final_text = f"Stopped after {max_tool_rounds} tool rounds without a final answer."
        else:
            final_text = self.client.content_to_text(msg.get("content")) or "(no content)"
            if all_tool_calls and final_text in ("", "(no content)", "(empty)", "(acknowledged)"):
                # Some tool-capable models occasionally return an empty message
                # after receiving tool results. Ask once for a text-only summary
                # grounded only in the verified evidence we already have.
                summary_messages = list(messages)
                summary_messages.append({
                    "role": "user",
                    "content": (
                        "The previous assistant response was empty. Using only the "
                        "verified tool results in this turn, answer the original user request. "
                        "Do not claim that any requested action happened unless a tool result proves it. "
                        "If part of the request remains undone, state that clearly."
                    ),
                })
                response = self.client.chat(messages=summary_messages, tools=None, max_tokens=512)
                fallback_text = self.client.extract_content(response)
                if (
                    fallback_text not in ("", "(no content)", "(empty)", "(acknowledged)")
                    and "<tool_call" not in fallback_text
                    and "<function=" not in fallback_text
                ):
                    final_text = fallback_text
                else:
                    verified = "; ".join(
                        entry["claim"] for entry in proof_log if entry.get("success") and entry.get("claim")
                    ) or "tool execution completed"
                    final_text = (
                        f"Verified: {verified}. The model did not provide a grounded final answer; "
                        "any requested action not listed here remains undone."
                    )
        # Append final assistant message to messages for history
        messages.append({"role": "assistant", "content": final_text})

        # Update persistent history (exclude system message)
        self.history = messages[1:]

        return AgentTurnResult(
            user_input=user_input,
            assistant_text=final_text,
            tool_calls=all_tool_calls,
            tool_results=tool_results,
            proof_log=proof_log,
            raw_messages=messages,
        )
