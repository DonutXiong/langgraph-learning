from __future__ import annotations

import operator
from pprint import pprint
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class QuizState(TypedDict):
    topic: str
    attempts: int
    score: int
    history: Annotated[list[str], operator.add]


def take_quiz(state: QuizState) -> dict:
    attempt = state.get("attempts", 0) + 1

    # 用固定分数模拟“第一次学不会，复习后提高”的流程。
    score = 55 if attempt == 1 else 88

    return {
        "attempts": attempt,
        "score": score,
        "history": [f"第 {attempt} 次测验得分: {score}"],
    }


def review_notes(state: QuizState) -> dict:
    return {
        "history": [
            f"分数 {state['score']} 偏低，回顾 {state['topic']} 的 State/Node/Edge 与条件边。"
        ]
    }


def should_continue(state: QuizState) -> Literal["review_notes", END]:
    if state["score"] >= 80:
        return END
    return "review_notes"


def build_graph():
    builder = StateGraph(QuizState)
    builder.add_node("take_quiz", take_quiz)
    builder.add_node("review_notes", review_notes)

    builder.add_edge(START, "take_quiz")
    builder.add_conditional_edges("take_quiz", should_continue)
    builder.add_edge("review_notes", "take_quiz")

    return builder.compile()


if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"topic": "LangGraph", "attempts": 0, "score": 0, "history": []})

    print("运行结果:")
    pprint(result)
