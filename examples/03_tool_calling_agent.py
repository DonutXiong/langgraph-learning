from __future__ import annotations

import argparse
import operator
import os
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, HumanMessage, SystemMessage
from langchain.tools import tool
from langgraph.graph import END, START, StateGraph


SYSTEM_PROMPT = (
    "你是一个擅长数学计算的助理。"
    "当问题适合工具计算时，优先调用工具，不要心算。"
)


@tool
def add(a: int, b: int) -> int:
    """计算两个整数的和。"""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """计算两个整数的积。"""
    return a * b


@tool
def divide(a: int, b: int) -> float:
    """计算 a 除以 b 的结果。"""
    return a / b


TOOLS = [add, multiply, divide]
TOOLS_BY_NAME = {tool.name: tool for tool in TOOLS}
MODEL_WITH_TOOLS = None


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


def load_model():
    load_dotenv()
    model_name = os.getenv("LANGCHAIN_MODEL", "openai:deepseek-chat")

    # 检查必要的 API Key
    if model_name.startswith("openai:") and not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("检测到 OpenAI 兼容模型，但未配置 OPENAI_API_KEY。")
    if model_name.startswith("anthropic:") and not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("检测到 Anthropic 模型，但未配置 ANTHROPIC_API_KEY。")

    # 获取基础 URL（对于 DeepSeek 等第三方 OpenAI 兼容服务）
    base_url = os.getenv("OPENAI_BASE_URL")

    # 构建模型配置
    model_config = {
        "model": model_name,
        "temperature": 0
    }

    # 如果提供了基础 URL，添加到配置中
    if base_url:
        model_config["base_url"] = base_url

    model = init_chat_model(**model_config)
    return model.bind_tools(TOOLS)


def get_model_with_tools():
    global MODEL_WITH_TOOLS
    if MODEL_WITH_TOOLS is None:
        MODEL_WITH_TOOLS = load_model()
    return MODEL_WITH_TOOLS


def call_model(state: AgentState) -> dict:
    response = get_model_with_tools().invoke(
        [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    )
    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def call_tools(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    tool_results = []

    for tool_call in last_message.tool_calls:
        tool = TOOLS_BY_NAME[tool_call["name"]]
        tool_results.append(tool.invoke(tool_call))

    return {"messages": tool_results}


def route_after_model(state: AgentState) -> Literal["call_tools", END]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "call_tools"
    return END


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("call_model", call_model)
    builder.add_node("call_tools", call_tools)

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", route_after_model)
    builder.add_edge("call_tools", "call_model")

    return builder.compile()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行一个最小 LangGraph 工具调用 Agent")
    parser.add_argument(
        "question",
        nargs="?",
        default="先算 (3 + 4) * 5，再除以 7，最后告诉我结果。",
        help="要交给 Agent 的问题",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    app = build_graph()

    # 生成Mermaid图
    png_data = app.get_graph().draw_mermaid_png()
    with open("3-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成流程图: 3-graph.png")

    try:
        result = app.invoke(
            {
                "messages": [HumanMessage(content=args.question)],
                "llm_calls": 0,
            }
        )
    except RuntimeError as exc:
        print(f"运行失败: {exc}")
        print("请先配置 .env 文件中的 API Key。")
        print("对于 DeepSeek:")
        print("1. 获取 DeepSeek API Key: https://platform.deepseek.com/api_keys")
        print("2. 在 .env 文件中设置 OPENAI_API_KEY=你的API密钥")
        print("3. 确保 OPENAI_BASE_URL=https://api.deepseek.com")
        raise SystemExit(1) from exc

    print(f"LLM 调用次数: {result['llm_calls']}")
    print()

    for message in result["messages"]:
        message.pretty_print()
