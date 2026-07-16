from typing import Any, Literal
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentDecision(BaseModel):
    decision_type: Literal["tool_call", "final_answer"]
    thought: str | None = None
    tool_call: ToolCall | None = None
    final_answer: str | None = None


class TrajectoryStep(BaseModel):
    step_id: int

    thought: str | None = None
    raw_llm_output: str

    action: str | None = None
    action_input: dict[str, Any] | None = None

    observation: str | None = None
    tool_status: str | None = None
    tool_error: str | None = None

    llm_latency_ms: float | None = None
    tool_latency_ms: float | None = None


class AgentResult(BaseModel):
    question: str
    final_answer: str
    status: Literal[
        "success",
        "max_steps_reached",
        "parse_failed",
        "llm_failed",
    ]
    steps: list[TrajectoryStep]