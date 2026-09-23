"""
calculator skill – Proof-First Personal Agent.

A safe math evaluation skill that only allows basic arithmetic.
No eval() of arbitrary strings – only a whitelist of safe operations.
"""

import ast
import operator
from typing import Dict, Any

from core.registry import skill
from core.tools import ToolResult


# Whitelist of safe operations
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

_SAFE_NAMES = {
    "abs": abs,
    "round": round,
    "max": max,
    "min": min,
    "sum": sum,
}


def _safe_eval(node):
    """Safely evaluate an AST node."""
    if isinstance(node, ast.Constant):  # Python 3.8+
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Only numeric constants allowed, got {type(node.value).__name__}")
    elif hasattr(ast, 'Num') and isinstance(node, ast.Num):  # Python < 3.8 fallback
        return node.n
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        return _SAFE_OPS[op_type](_safe_eval(node.left), _safe_eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return _SAFE_OPS[op_type](_safe_eval(node.operand))
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls allowed")
        func_name = node.func.id
        if func_name not in _SAFE_NAMES:
            raise ValueError(f"Unknown function: {func_name}")
        args = [_safe_eval(arg) for arg in node.args]
        return _SAFE_NAMES[func_name](*args)
    elif isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    else:
        raise ValueError(f"Unsupported expression type: {type(node).__name__}")


@skill(
    name="calculate",
    description="Evaluate a safe mathematical expression (basic arithmetic only).",
    schema={
        "name": "calculate",
        "description": "Evaluate a safe mathematical expression. Supports +, -, *, /, **, //, %, abs(), round(), max(), min(), sum().",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression to evaluate, e.g. '2 + 2' or 'abs(-5) * 3'"},
            },
            "required": ["expression"],
        },
    },
)
def calculate(expression: str) -> ToolResult:
    """Safely evaluate a mathematical expression."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree)
        return ToolResult(
            success=True,
            content=str(result),
            proof_claim=f"calculate evaluated: {expression} = {result}",
            proof_evidence={"expression": expression, "result": result},
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Error evaluating '{expression}': {str(e)}",
            proof_claim=f"calculate failed for: {expression}",
            proof_evidence={"expression": expression, "error": str(e)},
        )
