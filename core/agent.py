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


SYSTEM_PROMPT = """You are a Proof-First Personal Agent. Every claim you make must be backed by evidence.
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

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        max_tokens: int = 512,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:800]
            return {"error": f"HTTP {e.code}: {body}"}
        except Exception as e:
            return {"error": str(e)}

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
    def extract_content(response: Dict[str, Any]) -> str:
        """Get plain text content from a response."""
        msg = NebiusClient.extract_message(response)
        content = msg.get("content")
        if content is None:
            return "(acknowledged)"
        return content if content else "(empty)"

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
    """One-turn agent: user message → model → (optional) tools → model → result."""

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        base_url: str = None,
        memory_dir: str = None,
        timeout: int = 60,
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

    def run_turn(self, user_input: str, extra_system: str = None) -> AgentTurnResult:
        """Run one complete agent turn."""
        system = SYSTEM_PROMPT
        if extra_system:
            system += "\n" + extra_system

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_input},
        ]

        # Initial model call
        response1 = self.client.chat(
            messages=messages,
            tools=self.tools.schemas(),
            max_tokens=512,
        )

        msg1 = self.client.extract_message(response1)
        tool_calls = self.client.extract_tool_calls(response1)
        proof_log: List[Dict[str, Any]] = []
        tool_results: List[ToolResult] = []

        if tool_calls:
            # Append assistant message with tool_calls
            messages.append(msg1)

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

            # Final model call with tool results
            response2 = self.client.chat(
                messages=messages,
                tools=self.tools.schemas(),
                max_tokens=512,
            )
            final_text = self.client.extract_content(response2)
        else:
            final_text = msg1.get("content") or "(no content)"

        return AgentTurnResult(
            user_input=user_input,
            assistant_text=final_text,
            tool_calls=tool_calls,
            tool_results=tool_results,
            proof_log=proof_log,
            raw_messages=messages,
        )
