import json
import re

from agent.schemas import AgentDecision, ToolCall


class ParseError(ValueError):
    pass

####
# 设计思路：使用正则化进行关键词匹配（通过temperature软控制）
# 判断模型下一步动作，并返回对应的动作
####
def parse_agent_output(text: str) -> AgentDecision:
    final_match = re.search(
        r"Final Answer:\s*(.+)",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    thought_match = re.search(
        r"Thought:\s*(.*?)(?=\nAction:|\nFinal Answer:|$)",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    thought = (
        thought_match.group(1).strip()
        if thought_match
        else None
    )

    if final_match:
        return AgentDecision(
            decision_type="final_answer",
            thought=thought,
            final_answer=final_match.group(1).strip(),
        )

    action_match = re.search(
        r"Action:\s*([A-Za-z0-9_-]+)",
        text,
        flags=re.IGNORECASE,
    )
    input_match = re.search(
        r"Action Input:\s*(\{.*\})",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if not action_match:
        raise ParseError("Missing Action or Final Answer.")

    if not input_match:
        raise ParseError("Missing Action Input.")

    try:
        arguments = json.loads(input_match.group(1))  # 第一个捕获组的内容，只返回最内层的结果
    except json.JSONDecodeError as exc:
        raise ParseError(
            f"Invalid Action Input JSON: {exc}"
        ) from exc

    return AgentDecision(
        decision_type="tool_call",
        thought=thought,
        tool_call=ToolCall(
            name=action_match.group(1),
            arguments=arguments,
        ),
    )