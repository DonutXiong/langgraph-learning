from __future__ import annotations

from pprint import pprint

from langgraph.func import entrypoint, task


@task
def collect_core_concepts(topic: str) -> list[str]:
    if topic.lower() == "langgraph":
        return [
            "State: 图运行时共享的数据结构",
            "Node: 处理逻辑的函数",
            "Edge: 决定流程如何继续",
        ]
    return [
        f"{topic}: 先拆解核心概念",
        f"{topic}: 再找典型输入输出",
        f"{topic}: 最后整理实践场景",
    ]


@task
def build_practice_tasks(topic: str) -> list[str]:
    return [
        f"为 {topic} 写一个最小可运行示例",
        f"为 {topic} 增加条件分支",
        f"为 {topic} 增加一次循环或重试逻辑",
    ]


@entrypoint()
def build_study_card(topic: str) -> dict:
    core_concepts_future = collect_core_concepts(topic)
    practice_tasks_future = build_practice_tasks(topic)

    return {
        "topic": topic,
        "core_concepts": core_concepts_future.result(),
        "practice_tasks": practice_tasks_future.result(),
    }


if __name__ == "__main__":
    result = build_study_card.invoke("LangGraph")

    print("运行结果:")
    pprint(result)
