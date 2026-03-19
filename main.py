from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

EXAMPLES = [
    ("01", "基础 StateGraph", "examples/01_basic_state_graph.py"),
    ("02", "条件分支与循环", "examples/02_conditional_loop.py"),
    ("03", "带工具调用的 Agent", "examples/03_tool_calling_agent.py"),
    ("04", "Functional API 工作流", "examples/04_functional_api_workflow.py"),
]


def main() -> None:
    print("LangGraph 学习项目")
    print("=" * 24)
    print(f"项目目录: {PROJECT_ROOT}")
    print()
    print("建议学习顺序:")
    for index, title, script in EXAMPLES:
        print(f"{index}. {title:<18} -> python3 {script}")
    print()
    print("首次使用:")
    print("1. 复制 .env.example 为 .env")
    print("2. 安装依赖: python3 -m pip install -r requirements.txt")
    print("3. 先运行 examples/01_basic_state_graph.py")
    print()
    print("更多说明请阅读 README.md 与 docs/learning-path.md")


if __name__ == "__main__":
    main()
