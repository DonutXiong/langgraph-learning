from __future__ import annotations

import operator
import tempfile
import shutil
import json
from pathlib import Path
from pprint import pprint
from typing import Annotated, TypedDict
from datetime import datetime

from langgraph.checkpoint.memory import MemorySaver
# Note: FileSystemCheckpointer may require additional setup
# For demonstration, we'll create a simple mock filesystem checkpointer
from langgraph.graph import END, START, StateGraph


class LearningState(TypedDict):
    """学习状态，包含进度和笔记"""
    topic: str
    progress: int  # 学习进度 0-100
    notes: Annotated[list[str], operator.add]
    completed: bool


def study_topic(state: LearningState) -> dict:
    """学习主题内容"""
    topic = state["topic"]
    progress = state.get("progress", 0) + 25

    return {
        "progress": min(progress, 100),
        "notes": [f"学习了 {topic} 的基础概念"],
    }


def practice_exercises(state: LearningState) -> dict:
    """练习题目"""
    topic = state["topic"]
    progress = state.get("progress", 0) + 25

    return {
        "progress": min(progress, 100),
        "notes": [f"完成了 {topic} 的练习题"],
    }


def review_materials(state: LearningState) -> dict:
    """复习材料"""
    topic = state["topic"]
    progress = state.get("progress", 0) + 25

    return {
        "progress": min(progress, 100),
        "notes": [f"复习了 {topic} 的关键知识点"],
    }


def final_assessment(state: LearningState) -> dict:
    """最终评估"""
    progress = 100
    completed = progress >= 100

    return {
        "progress": progress,
        "notes": ["完成了所有学习任务！"],
        "completed": completed,
    }


def should_continue(state: LearningState) -> str:
    """决定是否继续学习"""
    if state.get("progress", 0) >= 100:
        return END
    return "practice_exercises"


def build_graph_with_memory(checkpointer=None):
    """构建带记忆功能的图"""
    builder = StateGraph(LearningState, checkpointer=checkpointer)

    builder.add_node("study_topic", study_topic)
    builder.add_node("practice_exercises", practice_exercises)
    builder.add_node("review_materials", review_materials)
    builder.add_node("final_assessment", final_assessment)

    builder.add_edge(START, "study_topic")
    builder.add_conditional_edges("study_topic", should_continue)
    builder.add_edge("practice_exercises", "review_materials")
    builder.add_edge("review_materials", "final_assessment")
    builder.add_edge("final_assessment", END)

    return builder.compile()


def demo_memory_checkpointer():
    """演示内存检查点"""
    print("=" * 60)
    print("演示 1: 内存检查点 (MemorySaver)")
    print("=" * 60)

    # 创建内存检查点
    memory = MemorySaver()
    app = build_graph_with_memory(memory)

    # 生成Mermaid图
    png_data = app.get_graph().draw_mermaid_png()
    with open("5-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成流程图: 5-graph.png")

    # 第一次运行
    print("\n第一次运行 (学习 Python):")
    config = {"configurable": {"thread_id": "student_1"}}
    result1 = app.invoke(
        {"topic": "Python", "progress": 0, "notes": [], "completed": False},
        config=config
    )
    print(f"进度: {result1['progress']}%, 笔记数量: {len(result1['notes'])}")

    # 检查保存的状态
    print("\n检查保存的检查点...")
    checkpoint = memory.get(config)
    if checkpoint:
        print(f"检查点存在，版本: {checkpoint['metadata']['checkpoint_version']}")

    # 从检查点恢复并继续
    print("\n从检查点恢复并继续执行:")
    result2 = app.invoke(
        {"topic": "继续学习"},  # 只提供更新字段
        config=config
    )
    print(f"最终进度: {result2['progress']}%, 完成: {result2['completed']}")
    print(f"所有笔记: {result2['notes']}")


def demo_filesystem_checkpointer():
    """演示文件系统检查点（概念演示）"""
    print("\n" + "=" * 60)
    print("演示 2: 文件系统检查点概念")
    print("=" * 60)

    print("文件系统检查点将状态保存到磁盘，支持:")
    print("1. 持久化存储 - 生存期超过进程")
    print("2. 分布式访问 - 多进程/多机器共享")
    print("3. 备份和恢复 - 定期备份检查点")
    print("4. 审计跟踪 - 保留历史状态")

    # 创建临时目录用于演示
    temp_dir = tempfile.mkdtemp(prefix="langgraph_checkpoints_")
    print(f"\n模拟检查点目录: {temp_dir}")

    try:
        # 使用内存检查点模拟文件系统行为
        memory = MemorySaver()
        app = build_graph_with_memory(memory)

        # 第一次运行
        print("\n模拟第一次运行 (学习 LangGraph):")
        config = {"configurable": {"thread_id": "student_2"}}
        result1 = app.invoke(
            {"topic": "LangGraph", "progress": 0, "notes": [], "completed": False},
            config=config
        )
        print(f"进度: {result1['progress']}%, 笔记: {result1['notes'][-1]}")

        # 模拟保存到文件系统
        print("\n模拟保存检查点到文件系统...")
        checkpoint_data = {
            "thread_id": config["configurable"]["thread_id"],
            "state": result1,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }

        checkpoint_file = Path(temp_dir) / f"checkpoint_{config['configurable']['thread_id']}.json"
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            import json
            json.dump(checkpoint_data, f, indent=2)

        print(f"检查点已保存到: {checkpoint_file.name}")

        # 模拟从文件系统恢复
        print("\n模拟从文件系统恢复检查点...")
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            loaded_checkpoint = json.load(f)

        print(f"恢复的检查点: {loaded_checkpoint['thread_id']}")
        print(f"时间戳: {loaded_checkpoint['timestamp']}")

        # 继续执行
        result2 = app.invoke(
            {"topic": "继续学习 LangGraph"},
            config=config
        )
        print(f"恢复后进度: {result2['progress']}%, 完成: {result2['completed']}")

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)
        print(f"\n已清理临时目录: {temp_dir}")


def demo_multiple_threads():
    """演示多线程/多会话"""
    print("\n" + "=" * 60)
    print("演示 3: 多线程/多会话支持")
    print("=" * 60)

    memory = MemorySaver()
    app = build_graph_with_memory(memory)

    # 多个独立的学习会话
    students = [
        {"id": "alice", "topic": "机器学习"},
        {"id": "bob", "topic": "数据分析"},
        {"id": "charlie", "topic": "Web开发"},
    ]

    for student in students:
        config = {"configurable": {"thread_id": student["id"]}}

        # 每个学生开始学习
        result = app.invoke(
            {"topic": student["topic"], "progress": 0, "notes": [], "completed": False},
            config=config
        )

        print(f"\n学生 {student['id']} 学习 {student['topic']}:")
        print(f"  进度: {result['progress']}%, 笔记: {result['notes'][-1]}")

        # 检查每个学生的检查点
        checkpoint = memory.get(config)
        if checkpoint:
            print(f"  检查点版本: {checkpoint['metadata']['checkpoint_version']}")


if __name__ == "__main__":
    print("LangGraph Checkpoint 与 Memory 示例 ★★☆☆")
    print("演示持久化、状态恢复和多会话支持")
    print()

    # 演示1: 内存检查点
    demo_memory_checkpointer()

    # 演示2: 文件系统检查点
    demo_filesystem_checkpointer()

    # 演示3: 多线程支持
    demo_multiple_threads()

    print("\n" + "=" * 60)
    print("关键概念总结:")
    print("1. MemorySaver: 内存中的检查点，适合短期会话")
    print("2. FileSystemCheckpointer: 文件系统检查点，适合持久化")
    print("3. thread_id: 用于区分不同会话/用户")
    print("4. 状态恢复: 可以从检查点恢复并继续执行")
    print("5. 配置管理: 使用config字典管理检查点")
    print("=" * 60)
