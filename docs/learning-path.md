# LangGraph 学习路线

## 第一阶段: 先建立直觉

运行 `examples/01_basic_state_graph.py`，先理解三件事：

- `State` 是整张图共享的数据快照
- `Node` 就是普通 Python 函数
- `Edge` 决定下一个执行点

建议你做两个小改动：

1. 给 state 再加一个字段，比如 `difficulty`
2. 新增一个节点，比如 `collect_examples`

## 第二阶段: 学会“为什么 LangGraph 不是普通 DAG”

运行 `examples/02_conditional_loop.py`，看下面两个能力：

- 条件路由
- 循环执行

这是 LangGraph 比单纯 DAG 更适合 Agent 的核心原因之一。

建议你尝试：

1. 把结束条件从 `score >= 80` 改成你自己的规则
2. 增加一个失败分支，比如超过 3 次后进入 `coach_feedback`

## 第三阶段: 看另一种写法

运行 `examples/04_functional_api_workflow.py`，重点理解：

- Graph API 更显式，适合你清楚知道节点和边的时候
- Functional API 更贴近普通 Python 代码，适合把现有流程渐进式迁移到 LangGraph

## 第四阶段: 进入 Agent

运行 `examples/03_tool_calling_agent.py`，观察一次典型循环：

1. 用户消息进入图
2. 模型判断是否要调用工具
3. 如果要调用工具，工具节点执行
4. 工具结果回到模型
5. 模型决定是继续还是结束

你可以重点打印 `messages` 看每一步的消息结构。

## 建议继续扩展的主题

- `checkpointer` 与持久化
- `interrupt` 与 human-in-the-loop
- `subgraph`
- 流式输出 `stream`
- LangSmith 追踪

## 推荐练习

1. 做一个“学习助手”图，输入知识点，输出学习计划
2. 做一个“资料整理”图，支持分类、总结、补充问题
3. 给 Agent 加一个本地工具，比如读取 Markdown 文件
