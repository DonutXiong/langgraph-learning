from __future__ import annotations

import operator
import time
import random
from typing import Annotated, TypedDict, Optional, Callable
from enum import Enum
from datetime import datetime
from dataclasses import dataclass

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"        # 可自动恢复
    MEDIUM = "medium"  # 需要简单干预
    HIGH = "high"      # 需要人工干预
    CRITICAL = "critical"  # 无法恢复


class RecoveryStrategy(Enum):
    """恢复策略"""
    RETRY = "retry"              # 重试相同操作
    FALLBACK = "fallback"        # 使用备用方案
    DEGRADE = "degrade"          # 降级服务
    ESCALATE = "escalate"        # 升级处理
    ABORT = "abort"              # 中止流程


@dataclass
class ErrorInfo:
    """错误信息"""
    error_id: str
    task_name: str
    error_type: str
    severity: ErrorSeverity
    message: str
    timestamp: str
    retry_count: int = 0
    recovery_strategy: Optional[RecoveryStrategy] = None
    resolved: bool = False


@dataclass
class RecoveryAction:
    """恢复动作"""
    action_id: str
    strategy: RecoveryStrategy
    description: str
    handler: Callable
    max_attempts: int = 3
    backoff_factor: float = 1.5  # 退避因子


class ResilientState(TypedDict):
    """弹性状态"""
    # 任务状态
    current_task: str
    task_input: dict
    task_output: dict
    task_history: Annotated[list[str], operator.add]

    # 错误管理
    errors: Annotated[list[ErrorInfo], operator.add]
    active_error: Optional[ErrorInfo]
    recovery_actions: Annotated[list[RecoveryAction], operator.add]

    # 恢复状态
    recovery_mode: bool
    retry_count: int
    max_retries: int

    # 监控指标
    start_time: float
    total_errors: int
    recovered_errors: int
    failed_errors: int


# ==================== 错误模拟函数 ====================
def simulate_network_error() -> Exception:
    """模拟网络错误"""
    errors = [
        ConnectionError("网络连接超时"),
        TimeoutError("请求超时"),
        ConnectionRefusedError("连接被拒绝")
    ]
    return random.choice(errors)


def simulate_data_error() -> Exception:
    """模拟数据错误"""
    errors = [
        ValueError("数据格式无效"),
        KeyError("缺少必要字段"),
        TypeError("类型不匹配")
    ]
    return random.choice(errors)


def simulate_resource_error() -> Exception:
    """模拟资源错误"""
    errors = [
        MemoryError("内存不足"),
        OSError("文件系统错误"),
        RuntimeError("资源不可用")
    ]
    return random.choice(errors)


def simulate_external_service_error() -> Exception:
    """模拟外部服务错误"""
    errors = [
        Exception("API服务不可用"),
        Exception("第三方服务超时"),
        Exception("认证失败")
    ]
    return random.choice(errors)


# ==================== 任务函数（包含错误） ====================
def fetch_data(state: ResilientState) -> dict:
    """获取数据任务（可能失败）"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 获取数据")

    # 模拟网络错误 (30% 概率)
    if random.random() < 0.3:
        raise simulate_network_error()

    time.sleep(0.1)
    data = {"source": "api", "records": 100, "status": "success"}

    return {
        "task_output": {"fetch_data": data},
        "task_history": ["数据获取成功"]
    }


def process_data(state: ResilientState) -> dict:
    """处理数据任务（可能失败）"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 处理数据")

    # 模拟数据处理错误 (25% 概率)
    if random.random() < 0.25:
        raise simulate_data_error()

    input_data = state.get("task_output", {}).get("fetch_data", {})
    processed = {
        "cleaned_records": input_data.get("records", 0),
        "transformations": ["清洗", "标准化", "验证"]
    }

    time.sleep(0.15)

    return {
        "task_output": {"process_data": processed},
        "task_history": ["数据处理成功"]
    }


def call_external_service(state: ResilientState) -> dict:
    """调用外部服务（可能失败）"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 调用外部服务")

    # 模拟外部服务错误 (40% 概率)
    if random.random() < 0.4:
        raise simulate_external_service_error()

    time.sleep(0.2)
    response = {
        "service": "validation",
        "result": "approved",
        "score": random.uniform(0.7, 0.95)
    }

    return {
        "task_output": {"external_service": response},
        "task_history": ["外部服务调用成功"]
    }


def save_results(state: ResilientState) -> dict:
    """保存结果（可能失败）"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 保存结果")

    # 模拟资源错误 (20% 概率)
    if random.random() < 0.2:
        raise simulate_resource_error()

    time.sleep(0.1)
    saved_data = {
        "location": "database",
        "timestamp": datetime.now().isoformat(),
        "size": "1.2MB"
    }

    return {
        "task_output": {"save_results": saved_data},
        "task_history": ["结果保存成功"]
    }


# ==================== 错误处理函数 ====================
def create_error_info(error: Exception, task_name: str) -> ErrorInfo:
    """创建错误信息"""
    error_type = type(error).__name__

    # 根据错误类型确定严重程度
    severity_map = {
        "ConnectionError": ErrorSeverity.MEDIUM,
        "TimeoutError": ErrorSeverity.MEDIUM,
        "ValueError": ErrorSeverity.LOW,
        "KeyError": ErrorSeverity.LOW,
        "MemoryError": ErrorSeverity.HIGH,
        "OSError": ErrorSeverity.HIGH,
        "RuntimeError": ErrorSeverity.MEDIUM,
        "Exception": ErrorSeverity.MEDIUM
    }

    severity = severity_map.get(error_type, ErrorSeverity.MEDIUM)

    return ErrorInfo(
        error_id=f"err_{int(time.time())}_{random.randint(1000, 9999)}",
        task_name=task_name,
        error_type=error_type,
        severity=severity,
        message=str(error),
        timestamp=datetime.now().isoformat()
    )


def select_recovery_strategy(error_info: ErrorInfo) -> RecoveryStrategy:
    """选择恢复策略"""
    # 根据错误严重程度选择策略
    if error_info.severity == ErrorSeverity.LOW:
        return RecoveryStrategy.RETRY
    elif error_info.severity == ErrorSeverity.MEDIUM:
        return random.choice([RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK])
    elif error_info.severity == ErrorSeverity.HIGH:
        return random.choice([RecoveryStrategy.DEGRADE, RecoveryStrategy.ESCALATE])
    else:  # CRITICAL
        return RecoveryStrategy.ABORT


def handle_error(state: ResilientState, error: Exception) -> dict:
    """处理错误"""
    task_name = state.get("current_task", "unknown")
    error_info = create_error_info(error, task_name)

    print(f"\n⚠️ 错误处理: {task_name}")
    print(f"  错误类型: {error_info.error_type}")
    print(f"  严重程度: {error_info.severity.value}")
    print(f"  错误信息: {error_info.message}")

    # 更新错误计数
    total_errors = state.get("total_errors", 0) + 1

    # 选择恢复策略
    strategy = select_recovery_strategy(error_info)
    error_info.recovery_strategy = strategy

    print(f"  恢复策略: {strategy.value}")

    # 检查重试次数
    retry_count = state.get("retry_count", 0) + 1
    max_retries = state.get("max_retries", 3)

    if retry_count > max_retries:
        print(f"  重试次数超限 ({retry_count}/{max_retries})，升级处理")
        strategy = RecoveryStrategy.ESCALATE
        error_info.recovery_strategy = strategy

    return {
        "errors": [error_info],
        "active_error": error_info,
        "recovery_mode": True,
        "retry_count": retry_count,
        "total_errors": total_errors,
        "task_history": [f"任务 {task_name} 失败: {error_info.message}"]
    }


# ==================== 恢复策略实现 ====================
def retry_strategy(state: ResilientState) -> dict:
    """重试策略"""
    error_info = state["active_error"]
    error_info.retry_count += 1

    print(f"  执行重试策略 (尝试 {error_info.retry_count})")

    # 模拟退避延迟
    delay = min(1.0, 0.1 * (1.5 ** error_info.retry_count))
    time.sleep(delay)

    return {
        "recovery_mode": False,
        "task_history": [f"重试任务 {error_info.task_name}"]
    }


def fallback_strategy(state: ResilientState) -> dict:
    """备用方案策略"""
    error_info = state["active_error"]
    task_name = error_info.task_name

    print(f"  执行备用方案策略")

    # 根据任务选择备用方案
    fallback_actions = {
        "fetch_data": "使用缓存数据",
        "process_data": "简化处理流程",
        "call_external_service": "使用本地验证",
        "save_results": "保存到临时文件"
    }

    fallback = fallback_actions.get(task_name, "跳过该任务")

    return {
        "recovery_mode": False,
        "task_output": {f"{task_name}_fallback": fallback},
        "task_history": [f"任务 {task_name} 使用备用方案: {fallback}"]
    }


def degrade_strategy(state: ResilientState) -> dict:
    """降级服务策略"""
    error_info = state["active_error"]

    print(f"  执行降级服务策略")

    # 标记为降级模式
    return {
        "recovery_mode": False,
        "task_output": {"degraded_mode": True, "degraded_task": error_info.task_name},
        "task_history": [f"任务 {error_info.task_name} 降级执行"]
    }


def escalate_strategy(state: ResilientState) -> dict:
    """升级处理策略（触发人工干预）"""
    error_info = state["active_error"]

    print(f"  执行升级处理策略")
    print(f"  需要人工干预，触发中断")

    # 触发中断等待人工干预
    raise interrupt("human_intervention_required")


def abort_strategy(state: ResilientState) -> dict:
    """中止流程策略"""
    error_info = state["active_error"]

    print(f"  执行中止流程策略")
    print(f"  🚨 严重错误，中止整个流程")

    return {
        "recovery_mode": False,
        "task_history": [f"流程中止: {error_info.message}"],
        "task_output": {"aborted": True, "reason": error_info.message}
    }


def human_intervention(state: ResilientState, decision: str) -> dict:
    """人工干预处理"""
    error_info = state["active_error"]

    print(f"  人工干预: {decision}")

    if decision == "retry":
        return retry_strategy(state)
    elif decision == "skip":
        return {
            "recovery_mode": False,
            "task_history": [f"人工跳过任务 {error_info.task_name}"],
            "active_error": None
        }
    elif decision == "fix_and_continue":
        return {
            "recovery_mode": False,
            "task_history": [f"人工修复后继续任务 {error_info.task_name}"],
            "active_error": None,
            "recovered_errors": state.get("recovered_errors", 0) + 1
        }
    else:  # abort
        return abort_strategy(state)


# ==================== 路由和恢复逻辑 ====================
def execute_recovery(state: ResilientState) -> dict:
    """执行恢复"""
    error_info = state["active_error"]
    if not error_info or not error_info.recovery_strategy:
        return {"recovery_mode": False}

    strategy = error_info.recovery_strategy

    strategy_handlers = {
        RecoveryStrategy.RETRY: retry_strategy,
        RecoveryStrategy.FALLBACK: fallback_strategy,
        RecoveryStrategy.DEGRADE: degrade_strategy,
        RecoveryStrategy.ABORT: abort_strategy
    }

    handler = strategy_handlers.get(strategy)
    if handler:
        return handler(state)
    else:
        # ESCALATE 策略通过中断处理
        return escalate_strategy(state)


def route_after_task(state: ResilientState) -> str:
    """任务后路由"""
    if state.get("recovery_mode", False):
        return "execute_recovery"

    current_task = state.get("current_task", "")

    task_flow = {
        "fetch_data": "process_data",
        "process_data": "call_external_service",
        "call_external_service": "save_results",
        "save_results": END
    }

    return task_flow.get(current_task, END)


def route_after_recovery(state: ResilientState) -> str:
    """恢复后路由"""
    error_info = state.get("active_error")
    if not error_info:
        return state.get("current_task", "fetch_data")  # 重新执行失败的任务

    # 根据恢复策略决定下一步
    strategy = error_info.recovery_strategy

    if strategy == RecoveryStrategy.ABORT:
        return END
    elif strategy == RecoveryStrategy.FALLBACK:
        # 备用方案后继续下一个任务
        task_flow = {
            "fetch_data": "process_data",
            "process_data": "call_external_service",
            "call_external_service": "save_results",
            "save_results": END
        }
        return task_flow.get(error_info.task_name, END)
    else:
        # 重试或降级后重新执行原任务
        return error_info.task_name


# ==================== 构建弹性图 ====================
def build_resilient_graph():
    """构建弹性图"""
    builder = StateGraph(ResilientState)

    # 添加任务节点
    builder.add_node("fetch_data", fetch_data)
    builder.add_node("process_data", process_data)
    builder.add_node("call_external_service", call_external_service)
    builder.add_node("save_results", save_results)

    # 添加错误处理和恢复节点
    builder.add_node("handle_error", handle_error)
    builder.add_node("execute_recovery", execute_recovery)

    # 设置初始边
    builder.add_edge(START, "fetch_data")

    # 任务执行流（带错误处理）
    task_nodes = ["fetch_data", "process_data", "call_external_service", "save_results"]
    for task_node in task_nodes:
        builder.add_edge(task_node, "handle_error")  # 错误处理边
        builder.add_conditional_edges(task_node, route_after_task)  # 正常流程边

    # 恢复后路由
    builder.add_conditional_edges("execute_recovery", route_after_recovery)

    # 错误处理后路由
    builder.add_conditional_edges("handle_error", lambda s: "execute_recovery")

    return builder.compile()


# ==================== 演示函数 ====================
def demo_basic_error_recovery():
    """演示基础错误恢复"""
    print("=" * 60)
    print("演示 1: 基础错误恢复")
    print("=" * 60)

    app = build_resilient_graph()

    # 生成Mermaid图
    png_data = app.get_graph().draw_mermaid_png()
    with open("11-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成流程图: 11-graph.png")

    print("开始弹性工作流...")
    print("任务有随机失败概率，系统会自动尝试恢复")
    print("-" * 40)

    result = app.invoke({
        "current_task": "fetch_data",
        "task_input": {},
        "task_output": {},
        "task_history": [],
        "errors": [],
        "active_error": None,
        "recovery_actions": [],
        "recovery_mode": False,
        "retry_count": 0,
        "max_retries": 3,
        "start_time": time.time(),
        "total_errors": 0,
        "recovered_errors": 0,
        "failed_errors": 0
    })

    print("-" * 40)
    print("工作流执行完成!")
    print(f"总错误数: {result['total_errors']}")
    print(f"恢复错误: {result.get('recovered_errors', 0)}")
    print(f"任务历史: {len(result['task_history'])} 条")

    if result['errors']:
        print("\n错误详情:")
        for error in result['errors'][-3:]:  # 显示最后3个错误
            status = "已恢复" if error.resolved else "未解决"
            print(f"  {error.task_name}: {error.error_type} - {status}")


def demo_retry_mechanism():
    """演示重试机制"""
    print("\n" + "=" * 60)
    print("演示 2: 重试机制")
    print("=" * 60)

    app = build_resilient_graph()

    print("测试重试机制...")
    print("网络任务有30%失败率，最多重试3次")
    print("-" * 40)

    results = []

    for i in range(5):
        print(f"\n测试 {i+1}:")
        result = app.invoke({
            "current_task": "fetch_data",
            "task_input": {},
            "task_output": {},
            "task_history": [],
            "errors": [],
            "active_error": None,
            "recovery_actions": [],
            "recovery_mode": False,
            "retry_count": 0,
            "max_retries": 3,
            "start_time": time.time(),
            "total_errors": 0,
            "recovered_errors": 0,
            "failed_errors": 0
        })

        results.append(result)

        errors = result['errors']
        if errors:
            last_error = errors[-1]
            print(f"  错误数: {len(errors)}")
            print(f"  最后错误重试次数: {last_error.retry_count}")
            print(f"  恢复策略: {last_error.recovery_strategy.value if last_error.recovery_strategy else '无'}")
        else:
            print(f"  无错误，一次成功")

    print("-" * 40)
    successful = sum(1 for r in results if r['task_output'].get('save_results'))
    print(f"成功率: {successful}/{len(results)} ({successful/len(results):.1%})")


def demo_fallback_strategies():
    """演示备用方案策略"""
    print("\n" + "=" * 60)
    print("演示 3: 备用方案策略")
    print("=" * 60)

    app = build_resilient_graph()

    print("测试不同任务的备用方案...")
    print("-" * 40)

    tasks = ["fetch_data", "process_data", "call_external_service", "save_results"]
    fallback_results = {}

    for task in tasks:
        print(f"\n测试任务: {task}")

        # 模拟该任务失败
        result = app.invoke({
            "current_task": task,
            "task_input": {},
            "task_output": {},
            "task_history": [],
            "errors": [],
            "active_error": None,
            "recovery_actions": [],
            "recovery_mode": False,
            "retry_count": 2,  # 模拟已经重试过
            "max_retries": 2,
            "start_time": time.time(),
            "total_errors": 0,
            "recovered_errors": 0,
            "failed_errors": 0
        })

        # 检查是否使用了备用方案
        fallback_key = f"{task}_fallback"
        used_fallback = fallback_key in result.get('task_output', {})

        fallback_results[task] = {
            "used_fallback": used_fallback,
            "fallback_value": result.get('task_output', {}).get(fallback_key) if used_fallback else None,
            "errors": len(result['errors'])
        }

        print(f"  使用备用方案: {used_fallback}")
        if used_fallback:
            print(f"  备用方案: {fallback_results[task]['fallback_value']}")

    print("-" * 40)
    print("备用方案测试完成:")
    for task, stats in fallback_results.items():
        status = "使用备用" if stats["used_fallback"] else "未使用"
        print(f"  {task}: {status}, 错误数: {stats['errors']}")


def demo_escalation_and_human_intervention():
    """演示升级处理和人工干预"""
    print("\n" + "=" * 60)
    print("演示 4: 升级处理和人工干预")
    print("=" * 60)

    app = build_resilient_graph()

    print("测试升级处理流程...")
    print("模拟严重错误，触发人工干预")
    print("-" * 40)

    try:
        # 模拟一个会触发升级处理的错误场景
        result = app.invoke({
            "current_task": "call_external_service",
            "task_input": {},
            "task_output": {},
            "task_history": [],
            "errors": [],
            "active_error": None,
            "recovery_actions": [],
            "recovery_mode": False,
            "retry_count": 3,  # 已经达到重试上限
            "max_retries": 3,
            "start_time": time.time(),
            "total_errors": 0,
            "recovered_errors": 0,
            "failed_errors": 0
        })
    except interrupt as e:
        print(f"  触发中断: {e.value}")
        print("  模拟人工干预决策...")

        # 模拟人工决策
        decisions = ["retry", "skip", "fix_and_continue", "abort"]
        decision = random.choice(decisions)
        print(f"  人工决策: {decision}")

        # 这里实际应该调用 human_intervention 函数
        print(f"  根据决策 '{decision}' 继续执行")

    print("-" * 40)
    print("人工干预演示完成")


def demo_error_metrics_and_monitoring():
    """演示错误指标和监控"""
    print("\n" + "=" * 60)
    print("演示 5: 错误指标和监控")
    print("=" * 60)

    app = build_resilient_graph()

    print("收集错误指标和性能数据...")
    print("-" * 40)

    runs = 10
    all_errors = []
    recovery_stats = {
        "retry": 0,
        "fallback": 0,
        "degrade": 0,
        "escalate": 0,
        "abort": 0
    }

    for i in range(runs):
        result = app.invoke({
            "current_task": "fetch_data",
            "task_input": {},
            "task_output": {},
            "task_history": [],
            "errors": [],
            "active_error": None,
            "recovery_actions": [],
            "recovery_mode": False,
            "retry_count": 0,
            "max_retries": 3,
            "start_time": time.time(),
            "total_errors": 0,
            "recovered_errors": 0,
            "failed_errors": 0
        })

        all_errors.extend(result['errors'])

        # 统计恢复策略
        for error in result['errors']:
            if error.recovery_strategy:
                strategy = error.recovery_strategy.value
                if strategy in recovery_stats:
                    recovery_stats[strategy] += 1

    print(f"\n运行 {runs} 次测试结果:")
    print(f"总错误数: {len(all_errors)}")
    print(f"平均每次运行错误数: {len(all_errors)/runs:.1f}")

    if all_errors:
        # 错误类型分布
        error_types = {}
        severities = {}
        for error in all_errors:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            severities[error.severity.value] = severities.get(error.severity.value, 0) + 1

        print(f"\n错误类型分布:")
        for err_type, count in error_types.items():
            print(f"  {err_type}: {count}次 ({count/len(all_errors):.1%})")

        print(f"\n严重程度分布:")
        for severity, count in severities.items():
            print(f"  {severity}: {count}次 ({count/len(all_errors):.1%})")

        print(f"\n恢复策略使用统计:")
        total_recoveries = sum(recovery_stats.values())
        for strategy, count in recovery_stats.items():
            if total_recoveries > 0:
                percentage = count / total_recoveries
                print(f"  {strategy}: {count}次 ({percentage:.1%})")

    print("-" * 40)
    print("监控数据收集完成")


if __name__ == "__main__":
    print("LangGraph 错误处理与恢复示例 ★★★★")
    print("演示错误检测、恢复策略、重试机制和弹性设计")
    print()

    # 演示1: 基础错误恢复
    demo_basic_error_recovery()

    # 演示2: 重试机制
    demo_retry_mechanism()

    # 演示3: 备用方案策略
    demo_fallback_strategies()

    # 演示4: 升级处理和人工干预
    demo_escalation_and_human_intervention()

    # 演示5: 错误指标和监控
    demo_error_metrics_and_monitoring()

    print("\n" + "=" * 60)
    print("关键概念总结:")
    print("1. 错误检测: 自动识别和分类错误")
    print("2. 恢复策略: RETRY, FALLBACK, DEGRADE, ESCALATE, ABORT")
    print("3. 重试机制: 退避算法和重试限制")
    print("4. 人工干预: 严重错误升级处理")
    print("5. 弹性设计: 系统在错误时继续运行")
    print("6. 监控指标: 错误统计和性能监控")
    print("=" * 60)

    print("\n实际应用场景:")
    print("• 微服务调用失败恢复")
    print("• 数据库连接异常处理")
    print("• 外部API服务降级")
    print("• 批处理作业错误恢复")
    print("• 实时系统容错设计")