# ReadMe

## 1～2周任务

- 实现一个简单的React框架
  - ReAct本身是一个提示词工程方法，通过给出`模型思考 -> 采取行动 -> 获取外界反馈`的循环实现回答准确性，任务成功率的提升。
  - ReAct的提示词设计仿照文章的设计逻辑进行。
  - 需要进行llm调用和行动的环境的搭建。
- 调用工具进行多轮问答，至少提供 3 个工具，能够实现动态决策，统计用不用工具的对比
  - 原文中的工具为`search`、`lookup`、`finish`,用来实现信息检索（调用维基百科API）问答
  - 决定仿照信息检索进行天气查询、路线规划、简单计算的工具
  - 天气查询：
    - 在穿衣决策方面，希望模型知道需要根据天气晴朗/下雨、温度高/低进行穿衣推荐
    - 如果模型没有工具，可能输出的会更笼统，比如当前是夏天，推荐穿羽绒服
  - 路线规划：
    - 去某个地方应该怎么走
  - 计算器：
    - 简单加减法

## 模型设计

```Unicode
用户问题
  ↓
LLM 生成 Thought
  ↓
决定是否调用工具
  ├── 不调用工具 → Final Answer
  └── 调用工具
         ↓
      Action + Action Input
         ↓
      执行工具
         ↓
      Observation
         ↓
      再次调用 LLM
```

## 文件结构

```Unicode
simple-react-agent/
├── README.md
├── requirements.txt
├── config.py
├── main.py
├── agent/
│   ├── react_agent.py
│   ├── prompt.py
│   ├── parser.py
│   └── llm_client.py
│
├── tools/
│   ├── base.py
│   ├── calculator.py
│   ├── weather_tool.py
│   ├── date_tool.py
│   ├── adress_tool.py
│   └── registry.py
├── evaluation/
│   ├── evaluator.py
│   ├── metrics.py
│   └── run_experiments.py
├── data/
│   └── test_set.json
├── outputs/
│   ├── trajectories/
│   ├── predictions/
│   └── results.csv
└── analysis/
    └── analyze_trajectories.py
```
