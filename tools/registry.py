from typing import Any
import time
from tools.base import BaseTool, ToolExecutionResult


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(
                f"Tool already registered: {tool.name}"
            )
        self._tools[tool.name] = tool

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> ToolExecutionResult:
        if name not in self._tools:
            return ToolExecutionResult(
                status="tool_not_found",
                output=f"Tool '{name}' does not exist.",
                error="tool_not_found",
            )

        tool = self._tools[name]
        start = time.perf_counter()

        try:
            output = tool.run(**arguments)
            status = "success"
            error = None
        except TypeError as exc:
            output = f"Invalid tool arguments: {exc}"
            status = "invalid_input"
            error = str(exc)
        except TimeoutError as exc:
            output = f"Tool timed out: {exc}"
            status = "timeout"
            error = str(exc)
        except Exception as exc:
            output = f"Tool execution failed: {exc}"
            status = "execution_error"
            error = str(exc)

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return ToolExecutionResult(
            status=status,
            output=str(output),
            error=error,
            latency_ms=latency_ms,
        )

    def describe_tools(self) -> str:
        return "\n".join(
            tool.get_description()
            for tool in self._tools.values()
        )

    def names(self) -> list[str]:
        return list(self._tools.keys())