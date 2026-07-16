from agent.react_agent import ReActAgent
from agent.llm_client import LLMClient
from config import AgentConfig
from tools.registry import register


def main() -> None:
    config = AgentConfig()
    llm = LLMClient(config)
    tools = register()  # 可用的登记器

    agent = ReActAgent(
        llm=llm,
        tool_registry=tools,
        config=config,
    )

    question = input("Question: ").strip()

    if not question:
        print("问题不能为空")
        return

    result = agent.run(question)

    print("\nFinal Answer:")
    print(result.final_answer)

    print("\nTool Calls:")
    for step in result.steps:
        if step.action:
            print(
                f"- {step.action}"
                f"({step.action_input})"
            )


if __name__ == "__main__":
    main()