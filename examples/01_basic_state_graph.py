from __future__ import annotations

import operator
from pprint import pprint
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class StudyState(TypedDict):
    topic: str
    notes: Annotated[list[str], operator.add]
    summary: str


def collect_foundation(state: StudyState) -> dict:
    topic = state["topic"]
    return {
        "notes": [
            f"{topic} 的核心组成是 State、Node、Edge。",
            "Node 负责处理逻辑，State 负责承载上下文。",
        ]
    }


def collect_patterns(state: StudyState) -> dict:
    topic = state["topic"]
    return {
        "notes": [
            f"{topic} 很适合有状态、可分支、可循环的工作流。",
            "Graph compile 之后才能 invoke 或 stream。",
        ]
    }


def summarize_notes(state: StudyState) -> dict:
    summary = " ".join(state["notes"])
    return {"summary": summary}


def build_graph():
    builder = StateGraph(StudyState)
    builder.add_node("collect_foundation", collect_foundation)
    builder.add_node("collect_patterns", collect_patterns)
    builder.add_node("summarize_notes", summarize_notes)

    builder.add_edge(START, "collect_foundation")
    builder.add_edge("collect_foundation", "collect_patterns")
    builder.add_edge("collect_patterns", "summarize_notes")
    builder.add_edge("summarize_notes", END)

    return builder.compile()


if __name__ == "__main__":
    app = build_graph()

    # 生成Mermaid图
    png_data = app.get_graph().draw_mermaid_png()
    with open("1-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成流程图: 1-graph.png")

    result = app.invoke({"topic": "LangGraph"})

    print("运行结果:")
    pprint(result)
