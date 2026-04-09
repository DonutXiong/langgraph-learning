from __future__ import annotations

import operator
import time
import json
import random
from typing import Annotated, TypedDict, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from langgraph.graph import END, START, StateGraph


class TraceLevel(Enum):
    """追踪级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TraceEvent:
    """追踪事件"""
    event_id: str
    timestamp: str
    level: TraceLevel
    component: str
    operation: str
    duration_ms: Optional[float] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    parent_event_id: Optional[str] = None
    trace_id: Optional[str] = None

    def to_dict(self):
        data = asdict(self)
        data["level"] = self.level.value
        return data


@dataclass
class TraceSession:
    """追踪会话"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    total_events: int = 0
    error_count: int = 0
    total_duration_ms: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class MockLangSmithClient:
    """模拟LangSmith客户端"""

    def __init__(self, api_key: Optional[str] = None, project: str = "langgraph-learning"):
        self.api_key = api_key or "mock-api-key"
        self.project = project
        self.sessions: Dict[str, TraceSession] = {}
        self.events: Dict[str, List[TraceEvent]] = {}
        self.export_dir = Path("./traces")
        self.export_dir.mkdir(exist_ok=True)

    def start_session(self, session_id: Optional[str] = None) -> str:
        """开始追踪会话"""
        if session_id is None:
            session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"

        session = TraceSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            metadata={"project": self.project, "client": "mock"}
        )

        self.sessions[session_id] = session
        self.events[session_id] = []

        print(f"[LangSmith] 开始会话: {session_id}")
        return session_id

    def end_session(self, session_id: str):
        """结束追踪会话"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.end_time = datetime.now().isoformat()
            session.total_events = len(self.events[session_id])
            session.error_count = sum(1 for e in self.events[session_id] if e.level == TraceLevel.ERROR)
            session.total_duration_ms = sum(e.duration_ms or 0 for e in self.events[session_id])

            print(f"[LangSmith] 结束会话: {session_id}")
            print(f"          事件数: {session.total_events}, 错误数: {session.error_count}")
            print(f"          总时长: {session.total_duration_ms:.1f}ms")

    def trace_event(self, session_id: str, event: TraceEvent):
        """记录追踪事件"""
        if session_id not in self.events:
            print(f"[LangSmith] 警告: 会话 {session_id} 不存在，自动创建")
            self.start_session(session_id)

        self.events[session_id].append(event)

        # 更新会话统计
        if session_id in self.sessions:
            self.sessions[session_id].total_events += 1
            if event.level == TraceLevel.ERROR:
                self.sessions[session_id].error_count += 1
            if event.duration_ms:
                self.sessions[session_id].total_duration_ms += event.duration_ms

        # 控制台输出
        level_colors = {
            TraceLevel.DEBUG: "\033[90m",      # 灰色
            TraceLevel.INFO: "\033[94m",       # 蓝色
            TraceLevel.WARNING: "\033[93m",    # 黄色
            TraceLevel.ERROR: "\033[91m",      # 红色
            TraceLevel.CRITICAL: "\033[95m"    # 紫色
        }
        reset = "\033[0m"

        color = level_colors.get(event.level, "\033[0m")
        duration_str = f" ({event.duration_ms:.1f}ms)" if event.duration_ms else ""

        print(f"{color}[LangSmith] {event.level.value.upper()}: {event.component}.{event.operation}{duration_str}{reset}")
        if event.error:
            print(f"          错误: {event.error}")

    def export_session(self, session_id: str, format: str = "json"):
        """导出会话数据"""
        if session_id not in self.sessions:
            raise ValueError(f"会话 {session_id} 不存在")

        session = self.sessions[session_id]
        session_events = self.events.get(session_id, [])

        export_data = {
            "session": asdict(session),
            "events": [e.to_dict() for e in session_events],
            "exported_at": datetime.now().isoformat(),
            "format": format
        }

        # 更新会话对象
        session_dict = asdict(session)
        session_dict["level"] = session.level.value if hasattr(session, "level") else "info"

        if format == "json":
            filename = self.export_dir / f"{session_id}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            print(f"[LangSmith] 导出会话到: {filename}")
            return str(filename)

        return None

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话摘要"""
        if session_id not in self.sessions:
            raise ValueError(f"会话 {session_id} 不存在")

        session = self.sessions[session_id]
        events = self.events.get(session_id, [])

        # 按组件统计
        component_stats = {}
        for event in events:
            component = event.component
            if component not in component_stats:
                component_stats[component] = {
                    "count": 0,
                    "total_duration_ms": 0,
                    "error_count": 0
                }
            component_stats[component]["count"] += 1
            if event.duration_ms:
                component_stats[component]["total_duration_ms"] += event.duration_ms
            if event.level == TraceLevel.ERROR:
                component_stats[component]["error_count"] += 1

        # 按级别统计
        level_stats = {}
        for event in events:
            level = event.level.value
            level_stats[level] = level_stats.get(level, 0) + 1

        return {
            "session_id": session_id,
            "duration": session.total_duration_ms,
            "total_events": session.total_events,
            "error_count": session.error_count,
            "component_stats": component_stats,
            "level_stats": level_stats,
            "start_time": session.start_time,
            "end_time": session.end_time
        }


class TracingState(TypedDict):
    """追踪状态"""
    # 追踪相关
    trace_session_id: str
    trace_events: Annotated[list[TraceEvent], operator.add]
    trace_enabled: bool

    # 业务数据
    input_data: dict
    processed_data: dict
    output_data: dict

    # 执行状态
    current_step: str
    execution_history: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]


def create_trace_decorator(client: MockLangSmithClient, session_id: str):
    """创建追踪装饰器"""

    def decorator(component: str, operation: str):
        def wrapper(func):
            def traced_function(state: TracingState, *args, **kwargs):
                if not state.get("trace_enabled", True):
                    return func(state, *args, **kwargs)

                event_id = f"event_{int(time.time()*1000)}_{random.randint(100, 999)}"
                start_time = time.time()

                # 创建事件
                event = TraceEvent(
                    event_id=event_id,
                    timestamp=datetime.now().isoformat(),
                    level=TraceLevel.INFO,
                    component=component,
                    operation=operation,
                    input_data=state.get("input_data", {}),
                    metadata={"function": func.__name__}
                )

                try:
                    # 执行函数
                    result = func(state, *args, **kwargs)

                    # 计算执行时间
                    event.duration_ms = (time.time() - start_time) * 1000
                    event.output_data = result

                    # 记录成功事件
                    client.trace_event(session_id, event)

                    # 添加到状态
                    if isinstance(result, dict):
                        result["trace_events"] = [event]
                    return result

                except Exception as e:
                    # 计算执行时间
                    event.duration_ms = (time.time() - start_time) * 1000
                    event.level = TraceLevel.ERROR
                    event.error = str(e)

                    # 记录错误事件
                    client.trace_event(session_id, event)

                    # 添加到状态
                    raise

            return traced_function
        return wrapper
    return decorator


# ==================== 业务函数（带追踪） ====================
def initialize_tracing(state: TracingState, client: MockLangSmithClient) -> dict:
    """初始化追踪"""
    session_id = client.start_session()
    trace_decorator = create_trace_decorator(client, session_id)

    return {
        "trace_session_id": session_id,
        "trace_enabled": True,
        "execution_history": [f"追踪会话已启动: {session_id}"]
    }


@create_trace_decorator(MockLangSmithClient(), "dummy")  # 装饰器会在运行时替换
def validate_input(state: TracingState) -> dict:
    """验证输入（带追踪）"""
    print("  验证输入数据...")
    time.sleep(0.05)

    input_data = state["input_data"]
    if not input_data.get("text"):
        raise ValueError("输入文本不能为空")

    validated = {
        "text_length": len(input_data.get("text", "")),
        "has_metadata": "metadata" in input_data,
        "valid": True
    }

    return {"processed_data": {"validation": validated}}


@create_trace_decorator(MockLangSmithClient(), "dummy")
def process_content(state: TracingState) -> dict:
    """处理内容（带追踪）"""
    print("  处理文本内容...")
    time.sleep(0.1)

    input_text = state["input_data"].get("text", "")
    processed = {
        "word_count": len(input_text.split()),
        "char_count": len(input_text),
        "processed_at": datetime.now().isoformat()
    }

    # 模拟随机错误
    if random.random() < 0.2:
        raise RuntimeError("内容处理失败")

    return {"processed_data": {"processing": processed}}


@create_trace_decorator(MockLangSmithClient(), "dummy")
def analyze_sentiment(state: TracingState) -> dict:
    """分析情感（带追踪）"""
    print("  分析情感倾向...")
    time.sleep(0.15)

    sentiments = ["positive", "neutral", "negative"]
    analysis = {
        "sentiment": random.choice(sentiments),
        "confidence": random.uniform(0.7, 0.95),
        "keywords": ["示例", "分析", "情感"]
    }

    return {"processed_data": {"sentiment_analysis": analysis}}


@create_trace_decorator(MockLangSmithClient(), "dummy")
def generate_summary(state: TracingState) -> dict:
    """生成摘要（带追踪）"""
    print("  生成内容摘要...")
    time.sleep(0.08)

    input_text = state["input_data"].get("text", "")
    if len(input_text) > 50:
        summary = input_text[:50] + "..."
    else:
        summary = input_text

    return {
        "output_data": {
            "summary": summary,
            "generated_at": datetime.now().isoformat()
        }
    }


@create_trace_decorator(MockLangSmithClient(), "dummy")
def finalize_output(state: TracingState) -> dict:
    """最终化输出（带追踪）"""
    print("  最终化处理结果...")
    time.sleep(0.03)

    all_data = {
        "input": state["input_data"],
        "processed": state["processed_data"],
        "output": state["output_data"],
        "trace_session": state["trace_session_id"]
    }

    return {"output_data": {"final": all_data}}


def handle_error(state: TracingState, error: Exception, client: MockLangSmithClient) -> dict:
    """错误处理（带追踪）"""
    error_event = TraceEvent(
        event_id=f"error_{int(time.time()*1000)}",
        timestamp=datetime.now().isoformat(),
        level=TraceLevel.ERROR,
        component="error_handler",
        operation="handle_error",
        error=str(error),
        metadata={"step": state.get("current_step", "unknown")}
    )

    client.trace_event(state["trace_session_id"], error_event)

    return {
        "errors": [str(error)],
        "execution_history": [f"错误处理: {error}"]
    }


# ==================== 构建追踪图 ====================
def build_traced_graph(client: MockLangSmithClient):
    """构建带追踪的图"""
    builder = StateGraph(TracingState)

    # 创建带追踪的函数
    def traced_validate_input(state):
        decorator = create_trace_decorator(client, state["trace_session_id"])
        traced_func = decorator("input", "validate")(validate_input.__wrapped__)
        return traced_func(state)

    def traced_process_content(state):
        decorator = create_trace_decorator(client, state["trace_session_id"])
        traced_func = decorator("processing", "content")(process_content.__wrapped__)
        return traced_func(state)

    def traced_analyze_sentiment(state):
        decorator = create_trace_decorator(client, state["trace_session_id"])
        traced_func = decorator("analysis", "sentiment")(analyze_sentiment.__wrapped__)
        return traced_func(state)

    def traced_generate_summary(state):
        decorator = create_trace_decorator(client, state["trace_session_id"])
        traced_func = decorator("output", "summary")(generate_summary.__wrapped__)
        return traced_func(state)

    def traced_finalize_output(state):
        decorator = create_trace_decorator(client, state["trace_session_id"])
        traced_func = decorator("output", "finalize")(finalize_output.__wrapped__)
        return traced_func(state)

    def traced_handle_error(state, error):
        return handle_error(state, error, client)

    # 添加节点
    builder.add_node("validate_input", traced_validate_input)
    builder.add_node("process_content", traced_process_content)
    builder.add_node("analyze_sentiment", traced_analyze_sentiment)
    builder.add_node("generate_summary", traced_generate_summary)
    builder.add_node("finalize_output", traced_finalize_output)

    # 设置边
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "process_content")
    builder.add_edge("process_content", "analyze_sentiment")
    builder.add_edge("analyze_sentiment", "generate_summary")
    builder.add_edge("generate_summary", "finalize_output")
    builder.add_edge("finalize_output", END)

    return builder.compile()


# ==================== 演示函数 ====================
def demo_basic_tracing():
    """演示基础追踪"""
    print("=" * 60)
    print("演示 1: 基础追踪功能")
    print("=" * 60)

    client = MockLangSmithClient()
    app = build_traced_graph(client)

    # 生成Mermaid图
    png_data = app.get_graph().draw_mermaid_png()
    with open("12-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成流程图: 12-graph.png")

    print("开始带追踪的工作流...")
    print("-" * 40)

    # 初始化追踪
    session_id = client.start_session()

    result = app.invoke({
        "trace_session_id": session_id,
        "trace_enabled": True,
        "trace_events": [],
        "input_data": {
            "text": "这是一个用于演示LangSmith追踪的示例文本。",
            "metadata": {"source": "demo", "version": "1.0"}
        },
        "processed_data": {},
        "output_data": {},
        "current_step": "start",
        "execution_history": [],
        "errors": []
    })

    # 结束会话
    client.end_session(session_id)

    print("-" * 40)
    print("工作流执行完成!")
    print(f"追踪会话: {session_id}")
    print(f"输出数据已生成")

    # 导出会话
    export_file = client.export_session(session_id)
    if export_file:
        print(f"追踪数据已导出到: {export_file}")


def demo_tracing_with_errors():
    """演示带错误的追踪"""
    print("\n" + "=" * 60)
    print("演示 2: 错误情况下的追踪")
    print("=" * 60)

    client = MockLangSmithClient()
    app = build_traced_graph(client)

    print("测试错误追踪...")
    print("内容处理有20%失败率")
    print("-" * 40)

    sessions = []

    for i in range(3):
        print(f"\n运行 {i+1}:")
        session_id = client.start_session(f"error_test_{i+1}")

        try:
            result = app.invoke({
                "trace_session_id": session_id,
                "trace_enabled": True,
                "trace_events": [],
                "input_data": {
                    "text": f"测试文本 {i+1}",
                    "metadata": {"test_run": i+1}
                },
                "processed_data": {},
                "output_data": {},
                "current_step": "start",
                "execution_history": [],
                "errors": []
            })
            print("  执行成功")
        except Exception as e:
            print(f"  执行失败: {e}")

        client.end_session(session_id)
        sessions.append(session_id)

    print("-" * 40)
    print("错误追踪测试完成")

    # 显示会话摘要
    for session_id in sessions:
        summary = client.get_session_summary(session_id)
        print(f"\n会话 {session_id} 摘要:")
        print(f"  事件数: {summary['total_events']}")
        print(f"  错误数: {summary['error_count']}")
        print(f"  总时长: {summary['duration']:.1f}ms")


def demo_trace_analysis():
    """演示追踪分析"""
    print("\n" + "=" * 60)
    print("演示 3: 追踪数据分析")
    print("=" * 60)

    client = MockLangSmithClient()

    print("生成并分析追踪数据...")
    print("-" * 40)

    # 运行多次收集数据
    all_summaries = []

    for i in range(5):
        session_id = client.start_session(f"analysis_{i+1}")
        app = build_traced_graph(client)

        try:
            result = app.invoke({
                "trace_session_id": session_id,
                "trace_enabled": True,
                "trace_events": [],
                "input_data": {
                    "text": f"分析测试文本 {i+1}，包含一些内容用于测试。",
                    "metadata": {"analysis_run": i+1}
                },
                "processed_data": {},
                "output_data": {},
                "current_step": "start",
                "execution_history": [],
                "errors": []
            })
        except Exception:
            pass  # 忽略错误，继续收集数据

        client.end_session(session_id)
        summary = client.get_session_summary(session_id)
        all_summaries.append(summary)

        # 导出数据
        client.export_session(session_id)

    print("-" * 40)
    print("数据分析结果:")

    # 计算平均指标
    total_events = sum(s["total_events"] for s in all_summaries)
    total_errors = sum(s["error_count"] for s in all_summaries)
    total_duration = sum(s["duration"] for s in all_summaries)

    print(f"  平均事件数: {total_events/len(all_summaries):.1f}")
    print(f"  平均错误数: {total_errors/len(all_summaries):.1f}")
    print(f"  平均时长: {total_duration/len(all_summaries):.1f}ms")
    print(f"  错误率: {total_errors/total_events:.1%}" if total_events > 0 else "错误率: N/A")

    # 组件性能分析
    component_stats = {}
    for summary in all_summaries:
        for component, stats in summary.get("component_stats", {}).items():
            if component not in component_stats:
                component_stats[component] = {"count": 0, "total_duration": 0, "errors": 0}
            component_stats[component]["count"] += stats["count"]
            component_stats[component]["total_duration"] += stats["total_duration_ms"]
            component_stats[component]["errors"] += stats["error_count"]

    print(f"\n组件性能分析:")
    for component, stats in component_stats.items():
        avg_duration = stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0
        error_rate = stats["errors"] / stats["count"] if stats["count"] > 0 else 0
        print(f"  {component}: {stats['count']}次调用, 平均{avg_duration:.1f}ms, 错误率{error_rate:.1%}")


def demo_trace_visualization():
    """演示追踪可视化"""
    print("\n" + "=" * 60)
    print("演示 4: 追踪数据可视化")
    print("=" * 60)

    client = MockLangSmithClient()

    print("生成可视化数据...")
    print("-" * 40)

    # 创建示例会话
    session_id = client.start_session("visualization_demo")
    app = build_traced_graph(client)

    # 运行工作流
    for _ in range(2):  # 运行两次
        try:
            result = app.invoke({
                "trace_session_id": session_id,
                "trace_enabled": True,
                "trace_events": [],
                "input_data": {
                    "text": "可视化演示文本，展示追踪数据。",
                    "metadata": {"demo": "visualization"}
                },
                "processed_data": {},
                "output_data": {},
                "current_step": "start",
                "execution_history": [],
                "errors": []
            })
        except Exception:
            pass

    client.end_session(session_id)

    # 生成可视化数据
    summary = client.get_session_summary(session_id)

    print(f"\n追踪会话 {session_id} 可视化数据:")
    print(f"时间线视图:")
    print("  开始 → 验证输入 → 处理内容 → 分析情感 → 生成摘要 → 最终化 → 结束")

    print(f"\n事件流:")
    events = client.events.get(session_id, [])
    for event in events[:10]:  # 显示前10个事件
        time_str = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')).strftime('%H:%M:%S.%f')[:-3]
        duration = f" ({event.duration_ms:.1f}ms)" if event.duration_ms else ""
        print(f"  [{time_str}] {event.component}.{event.operation}{duration} - {event.level.value}")

    if len(events) > 10:
        print(f"  ... 还有 {len(events)-10} 个事件")

    print(f"\n性能热点:")
    component_stats = summary.get("component_stats", {})
    for component, stats in component_stats.items():
        avg_time = stats["total_duration_ms"] / stats["count"] if stats["count"] > 0 else 0
        if avg_time > 50:  # 超过50ms的认为是热点
            print(f"  🔥 {component}: 平均 {avg_time:.1f}ms ({stats['count']}次调用)")

    # 导出详细数据
    export_file = client.export_session(session_id)
    print(f"\n详细数据已导出到: {export_file}")


def demo_production_ready_tracing():
    """演示生产环境就绪的追踪"""
    print("\n" + "=" * 60)
    print("演示 5: 生产环境追踪配置")
    print("=" * 60)

    print("生产环境追踪配置建议:")
    print("-" * 40)

    configs = [
        {
            "name": "开发环境",
            "level": "DEBUG",
            "sampling_rate": 1.0,
            "export_format": "json",
            "retention_days": 7,
            "features": ["详细日志", "完整追踪", "实时导出"]
        },
        {
            "name": "测试环境",
            "level": "INFO",
            "sampling_rate": 0.5,
            "export_format": "json",
            "retention_days": 30,
            "features": ["错误追踪", "性能监控", "批量导出"]
        },
        {
            "name": "生产环境",
            "level": "WARNING",
            "sampling_rate": 0.1,
            "export_format": "binary",
            "retention_days": 90,
            "features": ["错误告警", "性能指标", "安全审计"]
        }
    ]

    for config in configs:
        print(f"\n{config['name']}:")
        print(f"  追踪级别: {config['level']}")
        print(f"  采样率: {config['sampling_rate']:.0%}")
        print(f"  数据保留: {config['retention_days']}天")
        print(f"  特性: {', '.join(config['features'])}")

    print("\n" + "-" * 40)
    print("最佳实践:")
    print("1. 使用环境变量配置追踪")
    print("2. 实现追踪数据压缩")
    print("3. 设置合理的采样率")
    print("4. 定期清理旧数据")
    print("5. 监控追踪系统性能")
    print("6. 集成到现有监控系统")


if __name__ == "__main__":
    print("LangSmith 追踪与监控示例 ★★★☆")
    print("演示追踪、监控、调试和性能分析")
    print()

    # 演示1: 基础追踪
    demo_basic_tracing()

    # 演示2: 带错误的追踪
    demo_tracing_with_errors()

    # 演示3: 追踪分析
    demo_trace_analysis()

    # 演示4: 追踪可视化
    demo_trace_visualization()

    # 演示5: 生产环境配置
    demo_production_ready_tracing()

    print("\n" + "=" * 60)
    print("关键概念总结:")
    print("1. 追踪会话: 完整工作流的执行记录")
    print("2. 追踪事件: 单个操作的详细记录")
    print("3. 追踪级别: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    print("4. 性能监控: 执行时间、资源使用等指标")
    print("5. 错误追踪: 错误发生时的完整上下文")
    print("6. 数据分析: 统计分析和性能优化")
    print("=" * 60)

    print("\n实际应用场景:")
    print("• 调试复杂工作流")
    print("• 性能瓶颈分析")
    print("• 错误根本原因分析")
    print("• 系统监控和告警")
    print("• 合规性和审计")
    print("• 用户体验优化")

    print("\n注意: 此示例使用模拟的LangSmith客户端")
    print("实际使用时需要配置真实的LangSmith API密钥")
    print("并安装 langsmith 包: pip install langsmith")