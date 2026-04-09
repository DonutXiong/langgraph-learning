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
│   ├── 01_basic_state_graph.py          # 基础 StateGraph
│   ├── 02_conditional_loop.py           # 条件分支与循环
│   ├── 03_tool_calling_agent.py         # 带工具调用的 Agent
│   ├── 04_functional_api_workflow.py    # Functional API 工作流
│   ├── 05_checkpoint_memory.py          # 持久化与状态管理 ★★☆☆
│   ├── 06_stream_output.py              # 流式输出 ★★☆☆
│   ├── 07_interrupt_human_loop.py       # 中断与人工干预 ★★★☆
│   ├── 08_subgraph_modular.py           # 子图与模块化 ★★★☆
│   ├── 09_workflow_orchestration.py     # 工作流编排 ★★★☆
│   ├── 10_concurrent_nodes.py           # 并发执行 ★★★★
│   ├── 11_error_recovery.py             # 错误处理与恢复 ★★★★
│   └── 12_langsmith_tracing.py          # 追踪与监控 ★★★☆
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
```

配置 DeepSeek API Key（仅 Agent 示例需要）：
1. 获取 DeepSeek API Key: https://platform.deepseek.com/api_keys
2. 在 `.env` 文件中设置 `OPENAI_API_KEY=你的API密钥`

详细配置指南见 [DEEPSEEK_SETUP.md](DEEPSEEK_SETUP.md)。

如果你只想跑不依赖大模型的例子，可以先不配置 API Key，直接运行：

```bash
python examples/01_basic_state_graph.py
python examples/02_conditional_loop.py
python examples/04_functional_api_workflow.py
```

如果你要运行 Agent 示例，需要配置 DeepSeek API Key：

1. 获取 DeepSeek API Key: https://platform.deepseek.com/api_keys
2. 在 `.env` 文件中设置 `OPENAI_API_KEY=你的API密钥`
3. 然后运行：

```bash
python examples/03_tool_calling_agent.py
```

## 学习路径

### 基础篇 (01-04)
1. `01_basic_state_graph.py` - State、Node、Edge 基础概念
2. `02_conditional_loop.py` - 条件分支与循环
3. `04_functional_api_workflow.py` - Functional API 工作流
4. `03_tool_calling_agent.py` - 工具调用 Agent (需要 API Key)

### 中级篇 (05-08) ★★☆☆ ~ ★★★☆
5. `05_checkpoint_memory.py` - 持久化与状态管理
6. `06_stream_output.py` - 流式输出
7. `07_interrupt_human_loop.py` - 中断与人工干预
8. `08_subgraph_modular.py` - 子图与模块化

### 高级篇 (09-12) ★★★☆ ~ ★★★★
9. `09_workflow_orchestration.py` - 工作流编排
10. `10_concurrent_nodes.py` - 并发执行
11. `11_error_recovery.py` - 错误处理与恢复
12. `12_langsmith_tracing.py` - 追踪与监控

## 推荐学习顺序

按难度渐进学习：

1. **基础概念** (01-04): 掌握 LangGraph 核心概念
2. **中级特性** (05-08): 学习高级特性和模块化
3. **高级应用** (09-12): 实践复杂场景和最佳实践

详细学习路线见 `docs/learning-path.md`。

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

### 05 持久化与状态管理 ★★☆☆

学习如何保存和恢复图状态：

- `MemorySaver` 和 `FileSystemCheckpointer`
- 状态恢复和继续执行
- 多会话支持

### 06 流式输出 ★★☆☆

掌握实时输出和进度显示：

- `stream()` 方法的使用
- 实时进度显示
- 回调函数处理

### 07 中断与人工干预 ★★★☆

实现人工参与的工作流：

- `interrupt()` 机制
- Human-in-the-Loop 模式
- 错误处理与中断结合

### 08 子图与模块化 ★★★☆

构建可复用和模块化的系统：

- 子图创建和使用
- 嵌套图和模块组合
- 代码复用和共享组件

### 09 工作流编排 ★★★☆

实践复杂业务流程：

- 多步骤工作流设计
- 条件路由和错误恢复
- 检查点和持久化

### 10 并发执行 ★★★★

优化性能的并发模式：

- 顺序、线程池、进程池执行
- 异步并发处理
- 性能监控和优化

### 11 错误处理与恢复 ★★★★

构建弹性系统：

- 错误检测和分类
- 多种恢复策略
- 监控指标和告警

### 12 追踪与监控 ★★★☆

实现系统可观测性：

- 追踪会话和事件
- 性能分析和调试
- 生产环境监控配置

## 后续建议

- 根据实际需求选择合适的学习路径
- 将学到的模式应用到实际项目中
- 参考官方文档深入了解每个特性
- 参与社区讨论和分享经验
