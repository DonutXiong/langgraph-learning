# LangGraph 学习路线

## 学习路径概览

本学习路线按难度渐进设计，分为三个阶段：

1. **基础篇** (01-04): 掌握 LangGraph 核心概念
2. **中级篇** (05-08): 学习高级特性和模块化  
3. **高级篇** (09-12): 实践复杂场景和最佳实践

每个示例都有难度星级标识 (★☆☆☆ ~ ★★★★)，帮助你选择合适的学习起点。

## 第一阶段: 基础篇 - 建立直觉 (01-04)

### 01 基础 StateGraph ★☆☆☆
运行 `examples/01_basic_state_graph.py`，先理解三件事：

- `State` 是整张图共享的数据快照
- `Node` 就是普通 Python 函数
- `Edge` 决定流程如何继续

**练习建议:**
1. 给 state 再加一个字段，比如 `difficulty`
2. 新增一个节点，比如 `collect_examples`

### 02 条件分支与循环 ★★☆☆
运行 `examples/02_conditional_loop.py`，理解为什么 LangGraph 不是普通 DAG：

- 条件路由 (`add_conditional_edges`)
- 循环执行
- 状态驱动的流程控制

**练习建议:**
1. 把结束条件从 `score >= 80` 改成你自己的规则
2. 增加一个失败分支，比如超过 3 次后进入 `coach_feedback`

### 04 Functional API 工作流 ★★☆☆
运行 `examples/04_functional_api_workflow.py`，掌握另一种写法：

- `@entrypoint` 和 `@task` 装饰器
- Functional API vs Graph API
- 渐进式迁移现有代码

### 03 带工具调用的 Agent ★★★☆
运行 `examples/03_tool_calling_agent.py`，进入 Agent 开发：

- `messages` 状态和 `operator.add` 归约器
- 模型与工具交互循环
- 工具绑定和调用决策

**注意:** 需要配置 `.env` 文件中的 API Key

## 第二阶段: 中级篇 - 高级特性 (05-08)

### 05 持久化与状态管理 ★★☆☆
运行 `examples/05_checkpoint_memory.py`，学习状态持久化：

- `MemorySaver` 和 `FileSystemCheckpointer`
- 状态恢复和继续执行
- 多会话/多用户支持

### 06 流式输出 ★★☆☆  
运行 `examples/06_stream_output.py`，掌握实时输出：

- `stream()` 方法的使用
- 实时进度显示和回调处理
- 不同流模式对比

### 07 中断与人工干预 ★★★☆
运行 `examples/07_interrupt_human_loop.py`，实现人工参与：

- `interrupt()` 机制和工作流暂停
- Human-in-the-Loop 模式
- 错误处理与人工决策结合

### 08 子图与模块化 ★★★☆
运行 `examples/08_subgraph_modular.py`，构建模块化系统：

- 子图创建和嵌套使用
- 代码复用和组件共享
- 复杂系统分解策略

## 第三阶段: 高级篇 - 实战应用 (09-12)

### 09 工作流编排 ★★★☆
运行 `examples/09_workflow_orchestration.py`，实践复杂业务流程：

- 多步骤工作流设计模式
- 条件路由和错误恢复机制
- 检查点和持久化集成

### 10 并发执行 ★★★★
运行 `examples/10_concurrent_nodes.py`，优化系统性能：

- 顺序、线程池、进程池执行模式
- 异步并发处理
- 性能监控和动态并发控制

### 11 错误处理与恢复 ★★★★
运行 `examples/11_error_recovery.py`，构建弹性系统：

- 错误检测、分类和严重程度评估
- 多种恢复策略 (重试、降级、升级、中止)
- 监控指标和告警机制

### 12 追踪与监控 ★★★☆
运行 `examples/12_langsmith_tracing.py`，实现系统可观测性：

- 追踪会话和事件记录
- 性能分析和调试工具
- 生产环境监控配置

## 学习建议

### 按需学习
- 初学者: 从 01-04 开始，打好基础
- 中级开发者: 选择 05-08 中感兴趣的特性
- 高级开发者: 直接学习 09-12 的实战应用

### 实践项目
1. **学习助手**: 输入知识点，输出学习计划 (结合 01, 02, 09)
2. **数据管道**: ETL 流程自动化 (结合 05, 06, 10)  
3. **审批系统**: 人工干预工作流 (结合 07, 11)
4. **监控平台**: 系统可观测性 (结合 08, 12)

### 进阶资源
- 官方文档: https://langchain-ai.github.io/langgraph/
- GitHub 仓库: https://github.com/langchain-ai/langgraph
- 社区讨论: LangChain Discord 和论坛
- 实际项目: 参考开源项目中的 LangGraph 使用

## 持续学习

完成本学习路线后，你可以：

1. 根据实际需求设计复杂的 LangGraph 工作流
2. 实现弹性、可观测、高性能的系统
3. 参与社区贡献和知识分享
4. 将 LangGraph 应用到生产环境中

记住: 学习的最佳方式是实践。选择一个实际项目，应用你学到的知识，不断迭代和改进。