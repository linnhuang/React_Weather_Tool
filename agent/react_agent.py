from agent.parser import ParseError, parse_agent_output
from agent.prompt import build_system_prompt
from agent.schemas import AgentResult, TrajectoryStep
from config import AgentConfig
from tools.registry import ToolRegistry


class ReActAgent:
    def __init__(
        self,
        llm,
        tool_registry: ToolRegistry,
        config: AgentConfig,
    ) -> None:
        self.llm = llm
        self.tool_registry = tool_registry
        self.config = config
        # print(config)

    def run(self, question: str) -> AgentResult:
        # print("debug")
        messages = [
            {
                "role": "system",
                "content": build_system_prompt(
                    self.tool_registry.describe_tools()
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ]
        # print("debug")

        steps: list[TrajectoryStep] = []

        for step_id in range(1, self.config.max_steps + 1):
            print(f"Step {step_id}/{self.config.max_steps}")
            try:
                raw_output, llm_latency = self.llm.get_response(messages)
                # print("message")
                # raw_output = message or ""
                # print(raw_output)
                # print("debug")
            except Exception as exc:
                return AgentResult(
                    question=question,
                    final_answer="",
                    status="llm_failed",
                    steps=steps,
                )
            # print("debug")

            try:
                decision = parse_agent_output(raw_output)  # 模型开始尝试推理，一共有四个属性，可以直接调用
                # print("debug")
            except ParseError as exc:
                steps.append(
                    TrajectoryStep(
                        step_id=step_id,
                        raw_llm_output=raw_output,
                        tool_status="parse_error",
                        tool_error=str(exc),
                        llm_latency_ms=llm_latency,
                    )
                )
                print("debug")

                messages.append(
                    {
                        "role": "assistant",
                        "content": raw_output,
                    }
                )
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "当前回答不满足结构化要求"
                            "返回符合要求的结构再进行输出"
                        ),
                    }
                )
                continue
            # print(decision)
            if decision.decision_type == "final_answer":
                steps.append(
                    TrajectoryStep(
                        step_id=step_id,
                        thought=decision.thought,
                        raw_llm_output=raw_output,
                        llm_latency_ms=llm_latency,
                    )
                )

                print(f"Thought:{decision.thought}\nFinal Answer:{decision.final_answer}\n")

                return AgentResult(
                    question=question,
                    final_answer=decision.final_answer or "",
                    status="success",
                    steps=steps,
                )
            # print("debug")
            tool_call = decision.tool_call
            # print("debug")
            tool_result = self.tool_registry.execute(
                name=tool_call.name,
                arguments=tool_call.arguments,
            )
            # print(tool_result)
            # print("debug")
            steps.append(
                TrajectoryStep(
                    step_id=step_id,
                    thought=decision.thought,
                    raw_llm_output=raw_output,
                    action=tool_call.name,
                    action_input=tool_call.arguments,
                    observation=tool_result.output,
                    tool_status=tool_result.status,
                    tool_error=tool_result.error,
                    llm_latency_ms=llm_latency,
                    tool_latency_ms=tool_result.latency_ms,
                )
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": raw_output,
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Observation:\n{tool_result.output}"
                        f"\nTool Status: {tool_result.status}"
                    ),
                }
            )
            print(f"Thought:{decision.thought}\nAction:{tool_call.name}\nAction Input:{tool_call.arguments}\nObservation:{tool_result.output}\nTool Status:{tool_result.status}\nTool Error:{tool_result.error}\n")

        return AgentResult(
            question=question,
            final_answer="在规定的步数内无法完成任务",
            status="max_steps_reached",
            steps=steps,
        )