from __future__ import annotations

import operator
import time
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class StreamState(TypedDict):
    """流式处理状态"""
    input_text: str
    processed_chunks: Annotated[list[str], operator.add]
    current_chunk_index: int  # 当前正在处理的块索引
    progress: int  # 处理进度 0-100
    status: str


def split_into_chunks(state: StreamState) -> dict:
    """将输入文本分割成块"""
    text = state["input_text"]
    chunks = [text[i:i+10] for i in range(0, len(text), 10)]  # 每10字符一个块

    return {
        "processed_chunks": ["开始处理..."] + chunks,
        "current_chunk_index": 0,  # 从第一个块开始处理
        "progress": 10,
        "status": "分割完成"
    }


def process_chunk(state: StreamState) -> dict:
    """处理单个文本块（模拟耗时操作）"""
    chunks = state["processed_chunks"]
    current_index = state.get("current_chunk_index", 0)

    # 检查是否有块需要处理（跳过第一个"开始处理..."消息）
    if len(chunks) <= 1 or current_index >= len(chunks) - 1:
        return {"status": "无数据可处理"}

    # 获取当前要处理的块（跳过第一个"开始处理..."消息）
    chunk_to_process = chunks[current_index + 1]  # +1 跳过"开始处理..."

    # 模拟处理时间
    time.sleep(0.1)

    processed = f"已处理: '{chunk_to_process}'"

    # 计算进度
    total_chunks = len(state["input_text"]) // 10 + 1
    progress = min(100, 10 + ((current_index + 1) * 80 // total_chunks))

    return {
        "processed_chunks": [processed],
        "current_chunk_index": current_index + 1,  # 移动到下一个块
        "progress": progress,
        "status": f"处理中... ({current_index + 1}/{total_chunks})"
    }


def analyze_results(state: StreamState) -> dict:
    """分析处理结果"""
    current_index = state.get("current_chunk_index", 0)
    total_chunks = len(state["input_text"]) // 10 + 1

    return {
        "processed_chunks": [f"分析完成: 共处理了 {current_index} 个块 (总共 {total_chunks} 个块)"],
        "progress": 100,
        "status": "分析完成"
    }


def should_continue_processing(state: StreamState) -> str:
    """决定是否继续处理"""
    current_index = state.get("current_chunk_index", 0)

    # 计算总块数
    total_chunks = len(state["input_text"]) // 10 + 1

    if current_index >= total_chunks:
        return "analyze_results"
    return "process_chunk"


def build_stream_graph():
    """构建流式处理图"""
    builder = StateGraph(StreamState)

    builder.add_node("split_into_chunks", split_into_chunks)
    builder.add_node("process_chunk", process_chunk)
    builder.add_node("analyze_results", analyze_results)

    builder.add_edge(START, "split_into_chunks")
    builder.add_edge("split_into_chunks", "process_chunk")
    builder.add_conditional_edges("process_chunk", should_continue_processing)
    builder.add_edge("analyze_results", END)

    return builder.compile()


def demo_basic_stream():
    """演示基础流式输出"""
    print("=" * 60)
    print("演示 1: 基础流式输出")
    print("=" * 60)

    app = build_stream_graph()

    # 生成Mermaid图
    png_data = app.get_graph().draw_mermaid_png()
    with open("6-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成流程图: 6-graph.png")

    input_text = "LangGraph流式输出示例，展示实时处理进度。"

    print(f"输入文本: {input_text}")
    print("\n开始流式处理...")
    print("-" * 40)

    # 使用stream()获取流式结果
    stream = app.stream(
        {"input_text": input_text, "processed_chunks": [], "progress": 0, "status": "开始"},
        stream_mode="values"  # 只输出状态值
    )

    for chunk in stream:
        if "progress" in chunk:
            progress = chunk["progress"]
            status = chunk.get("status", "")

            # 显示进度条
            bar_length = 30
            filled = int(bar_length * progress / 100)
            bar = "#" * filled + "." * (bar_length - filled)

            print(f"进度: [{bar}] {progress}% - {status}")

            # 显示新处理的块
            if "processed_chunks" in chunk:
                new_chunks = chunk["processed_chunks"]
                if new_chunks and new_chunks[-1].startswith("已处理:"):
                    print(f"  处理: {new_chunks[-1]}")

    print("-" * 40)
    print("流式处理完成！")


def demo_stream_with_callbacks():
    """演示带回调的流式输出"""
    print("\n" + "=" * 60)
    print("演示 2: 带回调的流式输出")
    print("=" * 60)

    app = build_stream_graph()
    input_text = "这是一个更长的文本，用于演示回调函数的应用。"

    print(f"输入文本: {input_text}")

    # 定义回调函数
    def on_chunk(chunk):
        """处理每个流式块的回调"""
        if isinstance(chunk, dict) and "progress" in chunk:
            progress = chunk["progress"]

            # 只在进度更新时显示
            if hasattr(on_chunk, "last_progress") and on_chunk.last_progress == progress:
                return

            on_chunk.last_progress = progress

            # 简单进度显示
            print(f"回调收到进度更新: {progress}%")

            # 显示状态信息
            if "status" in chunk:
                print(f"  状态: {chunk['status']}")

            # 显示处理结果
            if "processed_chunks" in chunk:
                chunks = chunk["processed_chunks"]
                if chunks and chunks[-1].startswith("已处理:"):
                    print(f"  最新处理: {chunks[-1][:30]}...")

    on_chunk.last_progress = -1

    print("\n开始带回调的流式处理...")
    print("-" * 40)

    # 使用stream()并处理每个块
    stream = app.stream(
        {"input_text": input_text, "processed_chunks": [], "progress": 0, "status": "开始"},
        stream_mode="values"
    )

    for chunk in stream:
        on_chunk(chunk)

    print("-" * 40)
    print("回调处理完成！")


def demo_stream_modes():
    """演示不同的流式模式"""
    print("\n" + "=" * 60)
    print("演示 3: 不同的流式模式")
    print("=" * 60)

    app = build_stream_graph()
    input_text = "测试不同流模式"

    print("可用的流模式:")
    print("1. stream_mode='values' - 只输出状态值")
    print("2. stream_mode='updates' - 输出状态更新")
    print("3. stream_mode='debug' - 调试模式，输出详细信息")

    print("\n演示 'values' 模式:")
    print("-" * 40)

    stream = app.stream(
        {"input_text": input_text, "processed_chunks": [], "progress": 0, "status": "开始"},
        stream_mode="values"
    )

    count = 0
    for chunk in stream:
        count += 1
        if count <= 3:  # 只显示前3个块
            print(f"块 {count}: {chunk}")

    print(f"... 共 {count} 个流式块")
    print("-" * 40)


def demo_custom_stream_processor():
    """演示自定义流式处理器"""
    print("\n" + "=" * 60)
    print("演示 4: 自定义流式处理器")
    print("=" * 60)

    class StreamProcessor:
        """自定义流式处理器"""

        def __init__(self):
            self.start_time = None
            self.chunk_count = 0
            self.last_progress = 0

        def process(self, chunk):
            """处理流式块"""
            self.chunk_count += 1

            if self.start_time is None:
                self.start_time = time.time()

            current_time = time.time()
            elapsed = current_time - self.start_time

            if isinstance(chunk, dict) and "progress" in chunk:
                progress = chunk["progress"]

                # 只在进度变化时显示
                if progress != self.last_progress:
                    self.last_progress = progress

                    # 计算估计剩余时间
                    if progress > 0:
                        total_time = elapsed * 100 / progress
                        remaining = total_time - elapsed
                        eta = f", ETA: {remaining:.1f}s"
                    else:
                        eta = ""

                    print(f"[{elapsed:.1f}s] 进度: {progress}%{eta}")

    app = build_stream_graph()
    input_text = "自定义流式处理器示例文本。"

    print(f"输入文本: {input_text}")
    print("\n开始自定义流式处理...")
    print("-" * 40)

    processor = StreamProcessor()

    stream = app.stream(
        {"input_text": input_text, "processed_chunks": [], "progress": 0, "status": "开始"},
        stream_mode="values"
    )

    for chunk in stream:
        processor.process(chunk)

    print("-" * 40)
    print(f"处理完成！共处理 {processor.chunk_count} 个流式块")
    print(f"总耗时: {time.time() - processor.start_time:.2f} 秒")


if __name__ == "__main__":
    print("LangGraph 流式输出示例 ★★☆☆")
    print("演示实时输出、进度显示和回调处理")
    print()

    # 演示1: 基础流式输出
    demo_basic_stream()

    # 演示2: 带回调的流式输出
    demo_stream_with_callbacks()

    # 演示3: 不同的流式模式
    demo_stream_modes()

    # 演示4: 自定义流式处理器
    demo_custom_stream_processor()

    print("\n" + "=" * 60)
    print("关键概念总结:")
    print("1. stream() 方法: 替代 invoke() 进行流式处理")
    print("2. stream_mode 参数: values/updates/debug 模式")
    print("3. 实时进度显示: 适合长时间运行的任务")
    print("4. 回调函数: 自定义处理每个流式块")
    print("5. 性能考虑: 流式输出减少内存使用")
    print("=" * 60)

    print("\n实际应用场景:")
    print("- 实时聊天机器人响应")
    print("- 长文档处理进度显示")
    print("- 批量任务处理状态更新")
    print("- 用户界面实时反馈")