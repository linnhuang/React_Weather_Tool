from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class ToolExecutionResult(BaseModel):
    status: str
    output: str
    error: str | None = None
    latency_ms: float | None = None


class BaseTool(ABC):
    name: str
    description: str
    parameters: dict[str, Any]

    @abstractmethod
    def run(self, **kwargs: Any) -> str:
        raise NotImplementedError

    def get_description(self) -> str:
        return (
            f"- {self.name}: {self.description}\n"
            f"  Parameters: {self.parameters}"
        )