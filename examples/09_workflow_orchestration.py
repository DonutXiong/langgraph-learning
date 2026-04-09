from __future__ import annotations

import operator
import time
import random
from datetime import datetime
from typing import Annotated, Literal, TypedDict
from enum import Enum

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowState(TypedDict):
    """工作流状态"""
    # 工作流信息
    workflow_id: str
    workflow_name: str
    created_at: str
    status: TaskStatus

    # 任务相关
    current_task: str
    task_history: Annotated[list[str], operator.add]
    task_results: dict

    # 错误处理
    error_count: int
    error_messages: Annotated[list[str], operator.add]
    retry_attempts: dict

    # 性能指标
    start_time: float
    end_time: float
    execution_time: float

    # 检查点
    checkpoint_enabled: bool
    last_checkpoint: str


class TaskResult:
    """任务结果类"""

    def __init__(self, task_name: str, success: bool, result: any = None, error: str = None):
        self.task_name = task_name
        self.success = success
        self.result = result
        self.error = error
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "task_name": self.task_name,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp
        }


def initialize_workflow(state: WorkflowState) -> dict:
    """初始化工作流"""
    workflow_id = f"wf_{int(time.time())}_{random.randint(1000, 9999)}"

    return {
        "workflow_id": workflow_id,
        "created_at": datetime.now().isoformat(),
        "status": TaskStatus.IN_PROGRESS,
        "current_task": "data_collection",
        "task_history": [f"工作流 {workflow_id} 初始化完成"],
        "task_results": {},
        "error_count": 0,
        "start_time": time.time(),
        "checkpoint_enabled": True
    }


def collect_data(state: WorkflowState) -> dict:
    """收集数据任务"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 数据收集")

    # 模拟数据收集
    time.sleep(0.5)

    # 模拟随机失败
    if random.random() < 0.2:  # 20% 失败率
        raise Exception("数据源连接失败")

    data = {
        "sources": ["API", "数据库", "文件系统"],
        "records": random.randint(100, 1000),
        "size_mb": random.uniform(10.0, 100.0)
    }

    result = TaskResult("data_collection", True, data)

    return {
        "task_history": [f"数据收集完成: {data['records']} 条记录"],
        "task_results": {"data_collection": result.to_dict()},
        "current_task": "data_validation"
    }


def validate_data(state: WorkflowState) -> dict:
    """验证数据任务"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 数据验证")

    time.sleep(0.3)

    # 获取收集的数据
    collection_result = state["task_results"].get("data_collection", {})
    data = collection_result.get("result", {})

    if not data:
        raise Exception("无数据可验证")

    # 模拟验证逻辑
    issues = []
    if data.get("records", 0) < 50:
        issues.append("记录数不足")
    if data.get("size_mb", 0) > 200:
        issues.append("数据量过大")

    validation_result = {
        "valid": len(issues) == 0,
        "issues": issues,
        "checked_at": datetime.now().isoformat()
    }

    result = TaskResult("data_validation", True, validation_result)

    next_task = "data_processing" if validation_result["valid"] else "data_cleaning"

    return {
        "task_history": [f"数据验证完成: {'通过' if validation_result['valid'] else '失败'}"],
        "task_results": {"data_validation": result.to_dict()},
        "current_task": next_task
    }


def clean_data(state: WorkflowState) -> dict:
    """清理数据任务"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 数据清理")

    time.sleep(0.4)

    # 模拟清理过程
    cleaned_data = {
        "original_records": 500,
        "cleaned_records": 480,
        "removed_duplicates": 15,
        "fixed_errors": 5
    }

    result = TaskResult("data_cleaning", True, cleaned_data)

    return {
        "task_history": [f"数据清理完成: 移除 {cleaned_data['removed_duplicates']} 个重复项"],
        "task_results": {"data_cleaning": result.to_dict()},
        "current_task": "data_processing"
    }


def process_data(state: WorkflowState) -> dict:
    """处理数据任务"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 数据处理")

    time.sleep(0.6)

    # 模拟处理过程
    processing_result = {
        "algorithms_applied": ["标准化", "特征提取", "降维"],
        "processing_time_sec": 0.6,
        "output_features": random.randint(10, 50)
    }

    result = TaskResult("data_processing", True, processing_result)

    return {
        "task_history": [f"数据处理完成: 应用 {len(processing_result['algorithms_applied'])} 个算法"],
        "task_results": {"data_processing": result.to_dict()},
        "current_task": "model_training"
    }


def train_model(state: WorkflowState) -> dict:
    """训练模型任务"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 模型训练")

    time.sleep(1.0)  # 模拟耗时训练

    # 模拟训练结果
    training_result = {
        "model_type": "随机森林",
        "accuracy": round(random.uniform(0.85, 0.95), 3),
        "training_time_sec": 1.0,
        "parameters": {
            "n_estimators": 100,
            "max_depth": 10
        }
    }

    result = TaskResult("model_training", True, training_result)

    return {
        "task_history": [f"模型训练完成: 准确率 {training_result['accuracy']}"],
        "task_results": {"model_training": result.to_dict()},
        "current_task": "model_evaluation"
    }


def evaluate_model(state: WorkflowState) -> dict:
    """评估模型任务"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 模型评估")

    time.sleep(0.4)

    # 获取训练结果
    training_result = state["task_results"].get("model_training", {}).get("result", {})

    evaluation_result = {
        "test_accuracy": round(training_result.get("accuracy", 0.9) * 0.95, 3),
        "precision": round(random.uniform(0.88, 0.93), 3),
        "recall": round(random.uniform(0.86, 0.92), 3),
        "f1_score": round(random.uniform(0.87, 0.92), 3)
    }

    result = TaskResult("model_evaluation", True, evaluation_result)

    next_task = "deploy_model" if evaluation_result["test_accuracy"] > 0.85 else "optimize_model"

    return {
        "task_history": [f"模型评估完成: F1分数 {evaluation_result['f1_score']}"],
        "task_results": {"model_evaluation": result.to_dict()},
        "current_task": next_task
    }


def optimize_model(state: WorkflowState) -> dict:
    """优化模型任务"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 模型优化")

    time.sleep(0.5)

    # 模拟优化过程
    optimization_result = {
        "optimization_techniques": ["超参数调优", "特征选择"],
        "improvement": round(random.uniform(0.02, 0.05), 3),
        "optimized_accuracy": 0.89
    }

    result = TaskResult("model_optimization", True, optimization_result)

    return {
        "task_history": [f"模型优化完成: 提升 {optimization_result['improvement']}"],
        "task_results": {"model_optimization": result.to_dict()},
        "current_task": "deploy_model"
    }


def deploy_model(state: WorkflowState) -> dict:
    """部署模型任务"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 模型部署")

    time.sleep(0.3)

    deployment_result = {
        "environment": "生产环境",
        "deployment_time": datetime.now().isoformat(),
        "endpoint": f"https://api.example.com/models/{state['workflow_id']}",
        "version": "1.0.0"
    }

    result = TaskResult("model_deployment", True, deployment_result)

    return {
        "task_history": [f"模型部署完成: {deployment_result['endpoint']}"],
        "task_results": {"model_deployment": result.to_dict()},
        "current_task": "generate_report"
    }


def generate_report(state: WorkflowState) -> dict:
    """生成报告任务"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 生成报告")

    time.sleep(0.2)

    # 汇总所有任务结果
    all_results = state["task_results"]
    successful_tasks = [name for name, result in all_results.items() if result.get("success", False)]

    report = {
        "workflow_summary": {
            "workflow_id": state["workflow_id"],
            "total_tasks": len(all_results),
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(all_results) - len(successful_tasks),
            "error_count": state.get("error_count", 0)
        },
        "task_details": all_results,
        "generated_at": datetime.now().isoformat()
    }

    result = TaskResult("report_generation", True, report)

    return {
        "task_history": [f"报告生成完成: {len(successful_tasks)}/{len(all_results)} 个任务成功"],
        "task_results": {"report_generation": result.to_dict()},
        "current_task": "finalize_workflow",
        "status": TaskStatus.COMPLETED,
        "end_time": time.time(),
        "execution_time": time.time() - state.get("start_time", time.time())
    }


def finalize_workflow(state: WorkflowState) -> dict:
    """最终化工作流"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 任务: 工作流最终化")

    return {
        "task_history": ["工作流执行完成"],
        "status": TaskStatus.COMPLETED
    }


def handle_error(state: WorkflowState, error: Exception) -> dict:
    """错误处理"""
    error_count = state.get("error_count", 0) + 1
    error_msg = f"任务 {state.get('current_task', 'unknown')} 失败: {str(error)}"

    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 错误: {error_msg}")

    # 记录错误
    task_name = state.get("current_task", "unknown")
    result = TaskResult(task_name, False, error=str(error))

    # 检查重试次数
    retry_attempts = state.get("retry_attempts", {})
    attempts = retry_attempts.get(task_name, 0) + 1
    retry_attempts[task_name] = attempts

    if attempts <= 3:  # 最多重试3次
        print(f"  重试 {attempts}/3...")
        return {
            "error_count": error_count,
            "error_messages": [error_msg],
            "retry_attempts": retry_attempts,
            "task_results": {task_name: result.to_dict()},
            "task_history": [f"任务 {task_name} 失败，准备重试"]
        }
    else:
        print("  重试次数超限，工作流失败")
        return {
            "error_count": error_count,
            "error_messages": [error_msg],
            "retry_attempts": retry_attempts,
            "task_results": {task_name: result.to_dict()},
            "task_history": [f"任务 {task_name} 重试超限，工作流终止"],
            "status": TaskStatus.FAILED,
            "current_task": "workflow_failed"
        }


def route_workflow(state: WorkflowState) -> str:
    """工作流路由"""
    current_task = state.get("current_task", "")

    routing_map = {
        "data_collection": "validate_data",
        "data_validation": lambda s: "data_processing" if s.get("task_results", {}).get("data_validation", {}).get("result", {}).get("valid", False) else "data_cleaning",
        "data_cleaning": "data_processing",
        "data_processing": "model_training",
        "model_training": "model_evaluation",
        "model_evaluation": lambda s: "deploy_model" if s.get("task_results", {}).get("model_evaluation", {}).get("result", {}).get("test_accuracy", 0) > 0.85 else "optimize_model",
        "model_optimization": "deploy_model",
        "model_deployment": "generate_report",
        "generate_report": "finalize_workflow",
        "finalize_workflow": END,
        "workflow_failed": END
    }

    route = routing_map.get(current_task, END)

    if callable(route):
        return route(state)
    return route


def build_workflow_graph(checkpointer=None):
    """构建工作流图"""
    builder = StateGraph(WorkflowState, checkpointer=checkpointer)

    # 添加任务节点
    builder.add_node("initialize_workflow", initialize_workflow)
    builder.add_node("collect_data", collect_data)
    builder.add_node("validate_data", validate_data)
    builder.add_node("clean_data", clean_data)
    builder.add_node("process_data", process_data)
    builder.add_node("train_model", train_model)
    builder.add_node("evaluate_model", evaluate_model)
    builder.add_node("optimize_model", optimize_model)
    builder.add_node("deploy_model", deploy_model)
    builder.add_node("generate_report", generate_report)
    builder.add_node("finalize_workflow", finalize_workflow)

    # 添加错误处理节点
    builder.add_node("handle_error", handle_error)

    # 设置边
    builder.add_edge(START, "initialize_workflow")
    builder.add_conditional_edges("initialize_workflow", lambda s: "collect_data")

    # 主要工作流边
    builder.add_conditional_edges("collect_data", route_workflow)
    builder.add_conditional_edges("validate_data", route_workflow)
    builder.add_conditional_edges("clean_data", route_workflow)
    builder.add_conditional_edges("process_data", route_workflow)
    builder.add_conditional_edges("train_model", route_workflow)
    builder.add_conditional_edges("evaluate_model", route_workflow)
    builder.add_conditional_edges("optimize_model", route_workflow)
    builder.add_conditional_edges("deploy_model", route_workflow)
    builder.add_conditional_edges("generate_report", route_workflow)
    builder.add_edge("finalize_workflow", END)

    # 错误处理边
    for task_node in ["collect_data", "validate_data", "clean_data", "process_data",
                      "train_model", "evaluate_model", "optimize_model", "deploy_model"]:
        builder.add_edge(task_node, "handle_error")
        builder.add_conditional_edges("handle_error", lambda s: route_workflow(s) if s.get("status") != TaskStatus.FAILED else END)

    return builder.compile()


def demo_basic_workflow():
    """演示基础工作流"""
    print("=" * 60)
    print("演示 1: 基础工作流执行")
    print("=" * 60)

    app = build_workflow_graph()

    # 生成Mermaid图
    png_data = app.get_graph().draw_mermaid_png()
    with open("9-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成流程图: 9-graph.png")

    print("开始机器学习工作流...")
    print("-" * 40)

    result = app.invoke({
        "workflow_name": "机器学习流水线",
        "status": TaskStatus.PENDING,
        "task_history": [],
        "task_results": {},
        "error_count": 0,
        "error_messages": [],
        "retry_attempts": {},
        "checkpoint_enabled": False
    })

    print("-" * 40)
    print("工作流执行完成!")
    print(f"状态: {result['status'].value}")
    print(f"执行时间: {result.get('execution_time', 0):.2f} 秒")
    print(f"任务历史: {len(result['task_history'])} 条")
    print(f"错误次数: {result['error_count']}")


def demo_workflow_with_checkpoints():
    """演示带检查点的工作流"""
    print("\n" + "=" * 60)
    print("演示 2: 带检查点的工作流")
    print("=" * 60)

    memory = MemorySaver()
    app = build_workflow_graph(memory)

    config = {"configurable": {"thread_id": "workflow_001"}}

    print("开始带检查点的工作流...")
    print("模拟执行到一半时中断，然后恢复")
    print("-" * 40)

    # 第一次执行（模拟中途停止）
    print("第一次执行 (到数据处理):")
    state = {
        "workflow_name": "检查点演示",
        "status": TaskStatus.PENDING,
        "task_history": [],
        "task_results": {},
        "error_count": 0,
        "error_messages": [],
        "retry_attempts": {},
        "checkpoint_enabled": True
    }

    # 执行到数据处理
    try:
        for _ in range(4):  # 执行前4个任务
            state = app.invoke(state, config=config)
    except KeyboardInterrupt:
        print("\n模拟用户中断...")

    print(f"当前状态: {state.get('current_task', 'unknown')}")
    print(f"已完成任务: {list(state.get('task_results', {}).keys())}")

    # 检查检查点
    checkpoint = memory.get(config)
    if checkpoint:
        print(f"检查点已保存: 版本 {checkpoint['metadata']['checkpoint_version']}")

    # 恢复执行
    print("\n恢复执行...")
    result = app.invoke(state, config=config)

    print("-" * 40)
    print(f"最终状态: {result['status'].value}")
    print(f"总任务数: {len(result['task_results'])}")


def demo_error_recovery_workflow():
    """演示错误恢复工作流"""
    print("\n" + "=" * 60)
    print("演示 3: 错误恢复工作流")
    print("=" * 60)

    app = build_workflow_graph()

    print("演示错误处理和重试机制...")
    print("数据收集任务有20%失败率，最多重试3次")
    print("-" * 40)

    results = []

    for i in range(3):
        print(f"\n运行 {i+1}:")
        result = app.invoke({
            "workflow_name": f"错误恢复测试 {i+1}",
            "status": TaskStatus.PENDING,
            "task_history": [],
            "task_results": {},
            "error_count": 0,
            "error_messages": [],
            "retry_attempts": {},
            "checkpoint_enabled": False
        })

        results.append(result)

        print(f"  状态: {result['status'].value}")
        print(f"  错误次数: {result['error_count']}")
        print(f"  重试记录: {result.get('retry_attempts', {})}")

    print("-" * 40)
    print("错误恢复测试完成:")
    successful = sum(1 for r in results if r['status'] == TaskStatus.COMPLETED)
    print(f"成功: {successful}/{len(results)}")
    print(f"平均错误次数: {sum(r['error_count'] for r in results)/len(results):.1f}")


def demo_complex_routing():
    """演示复杂路由"""
    print("\n" + "=" * 60)
    print("演示 4: 复杂条件路由")
    print("=" * 60)

    app = build_workflow_graph()

    print("演示基于结果的条件路由:")
    print("1. 数据验证失败 → 数据清理 → 数据处理")
    print("2. 模型评估准确率<0.85 → 模型优化 → 模型部署")
    print("-" * 40)

    # 运行多次以观察不同路径
    paths = []

    for i in range(5):
        result = app.invoke({
            "workflow_name": f"路由测试 {i+1}",
            "status": TaskStatus.PENDING,
            "task_history": [],
            "task_results": {},
            "error_count": 0,
            "error_messages": [],
            "retry_attempts": {},
            "checkpoint_enabled": False
        })

        # 分析执行路径
        tasks = list(result['task_results'].keys())
        path = " → ".join(tasks)
        paths.append(path)

        print(f"运行 {i+1}: {path}")

    print("-" * 40)
    print("路径分析:")
    unique_paths = set(paths)
    for path in unique_paths:
        count = paths.count(path)
        print(f"  {count}次: {path}")


if __name__ == "__main__":
    print("LangGraph 工作流编排示例 ★★★☆")
    print("演示复杂工作流、错误恢复、检查点和条件路由")
    print()

    # 演示1: 基础工作流
    demo_basic_workflow()

    # 演示2: 带检查点的工作流
    demo_workflow_with_checkpoints()

    # 演示3: 错误恢复工作流
    demo_error_recovery_workflow()

    # 演示4: 复杂路由
    demo_complex_routing()

    print("\n" + "=" * 60)
    print("关键概念总结:")
    print("1. 工作流编排: 复杂业务流程的自动化")
    print("2. 错误恢复: 自动重试和错误处理")
    print("3. 条件路由: 基于结果动态选择路径")
    print("4. 检查点: 持久化和恢复执行状态")
    print("5. 任务管理: 任务状态跟踪和结果收集")
    print("=" * 60)

    print("\n实际应用场景:")
    print("• 机器学习流水线")
    print("• 数据ETL流程")
    print("• 业务审批流程")
    print("• 系统部署流程")
    print("• 批量数据处理")