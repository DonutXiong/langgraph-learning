# LangGraph Learning

这是一个面向入门和实践的 LangGraph 学习项目，重点不是堆功能，而是把几个核心概念拆成能直接运行的小例子。

## 你会学到什么

- `State` 如何在节点之间流转
- `Node` 和 `Edge` 怎么定义工作流
- 条件分支和循环如何实现
- Graph API 与 Functional API 的差别
- 一个最小可运行的工具调用 Agent 长什么样

## 项目结构

```text
.
├── README.md
├── docs/
│   └── learning-path.md
├── examples/
│   ├── 01_basic_state_graph.py
│   ├── 02_conditional_loop.py
│   ├── 03_tool_calling_agent.py
│   └── 04_functional_api_workflow.py
├── .env.example
├── requirements.txt
└── main.py
```

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
cp .env.example .env
```

如果你只想跑不依赖大模型的例子，可以先不配置 API Key，直接运行：

```bash
python3 examples/01_basic_state_graph.py
python3 examples/02_conditional_loop.py
python3 examples/04_functional_api_workflow.py
```

如果你要运行 Agent 示例，再补充 `.env` 中的模型配置：

```bash
python3 examples/03_tool_calling_agent.py
```

## 推荐学习顺序

1. `examples/01_basic_state_graph.py`
2. `examples/02_conditional_loop.py`
3. `examples/04_functional_api_workflow.py`
4. `examples/03_tool_calling_agent.py`

## 每个示例在学什么

### 01 基础 StateGraph

最小图结构，帮助你理解：

- `START -> 节点 -> 节点 -> END`
- 节点如何返回局部 state 更新
- reducer 如何把列表字段合并起来

### 02 条件分支与循环

展示 LangGraph 最有辨识度的一点：

- `add_conditional_edges`
- 根据 state 决定继续、回环还是结束

### 03 工具调用 Agent

这是最接近官方 quickstart 的学习示例，包含：

- `messages` 状态
- 模型节点
- 工具节点
- 模型决定是否继续调用工具

### 04 Functional API 工作流

当你不想显式画图，但又想保留 LangGraph 的任务编排能力时，可以看这个例子：

- `@entrypoint`
- `@task`
- 任务拆分与结果汇总

## 后续建议

- 把 `02_conditional_loop.py` 改造成你自己的业务流程
- 给 `03_tool_calling_agent.py` 增加新工具
- 下一步可继续学习 memory、checkpointer、interrupt、subgraph

详细学习路线见 `docs/learning-path.md`。
