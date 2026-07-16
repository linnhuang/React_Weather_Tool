import ast
import operator
from tools.base import BaseTool

# 输入可能有的操作
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def safe_evaluate(expression: str) -> float:
    node = ast.parse(expression, mode="eval").body

    def evaluate(current):
        if isinstance(current, ast.Constant):
            if not isinstance(current.value, int | float):
                raise ValueError("Only numeric constants are allowed.")
            return current.value

        if isinstance(current, ast.BinOp):
            operator_type = type(current.op)

            if operator_type not in _OPERATORS:
                raise ValueError("Unsupported binary operator.")

            left = evaluate(current.left)
            right = evaluate(current.right)

            return _OPERATORS[operator_type](left, right)

        if isinstance(current, ast.UnaryOp):
            operator_type = type(current.op)

            if operator_type not in _OPERATORS:
                raise ValueError("Unsupported unary operator.")

            return _OPERATORS[operator_type](
                evaluate(current.operand)
            )

        raise ValueError("Unsupported expression.")

    return evaluate(node)


class CalculatorTool(BaseTool):
    name = "calculator"
    description = (
        "Evaluate an exact arithmetic expression. "
        "Use it for calculations, percentages, powers, "
        "ratios, and multi-step arithmetic."
    )
    parameters = {
        "expression": "string"
    }

    def run(self, expression: str) -> str:
        result = safe_evaluate(expression)
        return str(result)