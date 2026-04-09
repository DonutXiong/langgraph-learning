from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

EXAMPLES = [
    ("01", "基础 StateGraph", "examples/01_basic_state_graph.py"),
    ("02", "条件分支与循环", "examples/02_conditional_loop.py"),
    ("03", "带工具调用的 Agent", "examples/03_tool_calling_agent.py"),
    ("04", "Functional API 工作流", "examples/04_functional_api_workflow.py"),
    ("05", "持久化与状态管理 ★★☆☆", "examples/05_checkpoint_memory.py"),
    ("06", "流式输出 ★★☆☆", "examples/06_stream_output.py"),
    ("07", "中断与人工干预 ★★★☆", "examples/07_interrupt_human_loop.py"),
    ("08", "子图与模块化 ★★★☆", "examples/08_subgraph_modular.py"),
    ("09", "工作流编排 ★★★☆", "examples/09_workflow_orchestration.py"),
    ("10", "并发执行 ★★★★", "examples/10_concurrent_nodes.py"),
    ("11", "错误处理与恢复 ★★★★", "examples/11_error_recovery.py"),
    ("12", "追踪与监控 ★★★☆", "examples/12_langsmith_tracing.py"),
]


def main() -> None:
    print("LangGraph 学习项目")
    print("=" * 24)
    print(f"项目目录: {PROJECT_ROOT}")
    print()
    print("建议学习顺序:")
    print("基础 (01-04):")
    for index, title, script in EXAMPLES[:4]:
        print(f"  {index}. {title:<25} -> python {script}")

    print("\n中级 (05-08):")
    for index, title, script in EXAMPLES[4:8]:
        print(f"  {index}. {title:<25} -> python {script}")

    print("\n高级 (09-12):")
    for index, title, script in EXAMPLES[8:]:
        print(f"  {index}. {title:<25} -> python {script}")

    print()
    print("首次使用:")
    print("1. 复制 .env.example 为 .env")
    print("2. 安装依赖: python -m pip install -r requirements.txt")
    print("3. 从 examples/01_basic_state_graph.py 开始")
    print()
    print("更多说明请阅读 README.md 与 docs/learning-path.md")


if __name__ == "__main__":
    main()
