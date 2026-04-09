from __future__ import annotations

import asyncio
import operator
import time
import random
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Annotated, TypedDict, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from langgraph.graph import END, START, StateGraph
from langgraph.constants import Send


@dataclass
class TaskResult:
    """任务结果数据类"""
    task_id: str
    task_name: str
    status: str  # pending, running, completed, failed
    result: Any
    error: str = None
    start_time: float = None
    end_time: float = None
    duration: float = None

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration
        }


class ConcurrentState(TypedDict):
    """并发执行状态"""
    # 任务管理
    task_queue: List[str]
    running_tasks: Dict[str, TaskResult]
    completed_tasks: Annotated[List[TaskResult], operator.add]
    failed_tasks: Annotated[List[TaskResult], operator.add]

    # 执行控制
    max_concurrent: int
    timeout_seconds: float
    execution_mode: str  # sequential, thread, process, async

    # 结果汇总
    final_results: Dict[str, Any]
    execution_stats: Dict[str, Any]


def create_tasks(state: ConcurrentState) -> dict:
    """创建并发任务"""
    task_types = [
        "data_fetch", "data_process", "model_inference",
        "file_io", "network_request", "cpu_computation"
    ]

    num_tasks = random.randint(8, 15)
    tasks = [f"{task_types[i % len(task_types)]}_{i}" for i in range(num_tasks)]

    return {
        "task_queue": tasks,
        "running_tasks": {},
        "completed_tasks": [],
        "failed_tasks": [],
        "execution_stats": {
            "total_tasks": num_tasks,
            "created_at": datetime.now().isoformat()
        }
    }


def simulate_task(task_name: str, task_id: str) -> TaskResult:
    """模拟任务执行"""
    start_time = time.time()
    result = TaskResult(task_id, task_name, "running", None, None, start_time)

    try:
        # 模拟不同类型的任务耗时
        if "data_fetch" in task_name:
            time.sleep(random.uniform(0.1, 0.3))  # I/O密集型
            task_result = {"records": random.randint(100, 1000), "source": "database"}
        elif "data_process" in task_name:
            time.sleep(random.uniform(0.2, 0.4))  # CPU密集型
            task_result = {"processed": True, "algorithm": "normalization"}
        elif "model_inference" in task_name:
            time.sleep(random.uniform(0.3, 0.6))  # 计算密集型
            task_result = {"prediction": random.random(), "confidence": random.uniform(0.7, 0.95)}
        elif "file_io" in task_name:
            time.sleep(random.uniform(0.1, 0.2))  # I/O密集型
            task_result = {"file_size": random.randint(1024, 10240), "operation": "read/write"}
        elif "network_request" in task_name:
            time.sleep(random.uniform(0.2, 0.5))  # 网络密集型
            task_result = {"status_code": 200, "response_time": random.uniform(0.1, 0.3)}
        elif "cpu_computation" in task_name:
            # 模拟CPU计算
            for _ in range(100000):
                _ = random.random() * random.random()
            time.sleep(0.1)
            task_result = {"computation": "completed", "iterations": 100000}
        else:
            time.sleep(0.1)
            task_result = {"type": "generic", "completed": True}

        # 模拟随机失败
        if random.random() < 0.1:  # 10%失败率
            raise Exception(f"任务 {task_name} 执行失败")

        result.status = "completed"
        result.result = task_result

    except Exception as e:
        result.status = "failed"
        result.error = str(e)
        result.result = None

    finally:
        result.end_time = time.time()
        result.duration = result.end_time - result.start_time

    return result


async def simulate_async_task(task_name: str, task_id: str) -> TaskResult:
    """模拟异步任务执行"""
    start_time = time.time()
    result = TaskResult(task_id, task_name, "running", None, None, start_time)

    try:
        # 模拟异步操作
        if "network_request" in task_name:
            await asyncio.sleep(random.uniform(0.1, 0.3))
            task_result = {"async": True, "network": "completed"}
        elif "data_fetch" in task_name:
            await asyncio.sleep(random.uniform(0.05, 0.15))
            task_result = {"async": True, "data": "fetched"}
        else:
            await asyncio.sleep(random.uniform(0.1, 0.2))
            task_result = {"async": True, "generic": "completed"}

        # 模拟随机失败
        if random.random() < 0.1:
            raise Exception(f"异步任务 {task_name} 失败")

        result.status = "completed"
        result.result = task_result

    except Exception as e:
        result.status = "failed"
        result.error = str(e)
        result.result = None

    finally:
        result.end_time = time.time()
        result.duration = result.end_time - result.start_time

    return result


def execute_sequential(state: ConcurrentState) -> dict:
    """顺序执行任务"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 模式: 顺序执行")

    task_queue = state["task_queue"].copy()
    completed = []
    failed = []

    for i, task_name in enumerate(task_queue):
        task_id = f"seq_{i}"
        print(f"  执行任务 {i+1}/{len(task_queue)}: {task_name}")

        result = simulate_task(task_name, task_id)

        if result.status == "completed":
            completed.append(result)
        else:
            failed.append(result)

    return {
        "completed_tasks": completed,
        "failed_tasks": failed,
        "task_queue": [],
        "execution_stats": {
            **state.get("execution_stats", {}),
            "mode": "sequential",
            "total_time": sum(t.duration for t in completed + failed)
        }
    }


def execute_threaded(state: ConcurrentState) -> dict:
    """线程池并发执行"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 模式: 线程池并发")
    print(f"  最大并发数: {state.get('max_concurrent', 4)}")

    task_queue = state["task_queue"].copy()
    max_workers = state.get("max_concurrent", 4)

    completed = []
    failed = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_task = {}
        for i, task_name in enumerate(task_queue):
            task_id = f"thread_{i}"
            future = executor.submit(simulate_task, task_name, task_id)
            future_to_task[future] = (task_name, task_id)

        # 收集结果
        for future in future_to_task:
            task_name, task_id = future_to_task[future]
            try:
                result = future.result(timeout=state.get("timeout_seconds", 10.0))
                if result.status == "completed":
                    completed.append(result)
                else:
                    failed.append(result)
            except Exception as e:
                failed_task = TaskResult(
                    task_id, task_name, "failed", None,
                    f"执行超时或异常: {str(e)}", time.time(), time.time(), 0
                )
                failed.append(failed_task)

    return {
        "completed_tasks": completed,
        "failed_tasks": failed,
        "task_queue": [],
        "execution_stats": {
            **state.get("execution_stats", {}),
            "mode": "threaded",
            "max_workers": max_workers,
            "total_time": max((t.duration for t in completed + failed), default=0)
        }
    }


def execute_process(state: ConcurrentState) -> dict:
    """进程池并发执行"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 模式: 进程池并发")
    print(f"  注意: 进程池适合CPU密集型任务")

    task_queue = state["task_queue"].copy()
    max_workers = min(state.get("max_concurrent", 4), 4)  # 限制进程数

    completed = []
    failed = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {}
        for i, task_name in enumerate(task_queue):
            if "cpu_computation" in task_name or "data_process" in task_name:
                task_id = f"process_{i}"
                future = executor.submit(simulate_task, task_name, task_id)
                future_to_task[future] = (task_name, task_id)

        for future in future_to_task:
            task_name, task_id = future_to_task[future]
            try:
                result = future.result(timeout=state.get("timeout_seconds", 15.0))
                if result.status == "completed":
                    completed.append(result)
                else:
                    failed.append(result)
            except Exception as e:
                failed_task = TaskResult(
                    task_id, task_name, "failed", None,
                    f"进程执行失败: {str(e)}", time.time(), time.time(), 0
                )
                failed.append(failed_task)

    return {
        "completed_tasks": completed,
        "failed_tasks": failed,
        "task_queue": [t for t in task_queue if t not in [tr.task_name for tr in completed + failed]],
        "execution_stats": {
            **state.get("execution_stats", {}),
            "mode": "process",
            "max_workers": max_workers,
            "total_time": max((t.duration for t in completed + failed), default=0)
        }
    }


async def execute_async(state: ConcurrentState) -> dict:
    """异步并发执行"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 模式: 异步并发")

    task_queue = state["task_queue"].copy()
    tasks = []

    for i, task_name in enumerate(task_queue):
        task_id = f"async_{i}"
        tasks.append(simulate_async_task(task_name, task_id))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    completed = []
    failed = []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            failed_task = TaskResult(
                f"async_{i}", task_queue[i], "failed", None,
                f"异步执行异常: {str(result)}", time.time(), time.time(), 0
            )
            failed.append(failed_task)
        elif result.status == "completed":
            completed.append(result)
        else:
            failed.append(result)

    return {
        "completed_tasks": completed,
        "failed_tasks": failed,
        "task_queue": [],
        "execution_stats": {
            **state.get("execution_stats", {}),
            "mode": "async",
            "total_time": max((t.duration for t in completed + failed), default=0)
        }
    }


def aggregate_results(state: ConcurrentState) -> dict:
    """聚合任务结果"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 聚合任务结果...")

    all_tasks = state["completed_tasks"] + state["failed_tasks"]
    successful = [t for t in state["completed_tasks"] if t.status == "completed"]
    failed = state["failed_tasks"]

    # 计算统计信息
    total_time = sum(t.duration for t in all_tasks if t.duration)
    avg_time = total_time / len(all_tasks) if all_tasks else 0
    max_time = max((t.duration for t in all_tasks if t.duration), default=0)
    min_time = min((t.duration for t in all_tasks if t.duration), default=0)

    # 按任务类型分组
    task_types = {}
    for task in all_tasks:
        task_type = task.task_name.split("_")[0]
        if task_type not in task_types:
            task_types[task_type] = {"total": 0, "success": 0, "total_time": 0}
        task_types[task_type]["total"] += 1
        if task.status == "completed":
            task_types[task_type]["success"] += 1
        if task.duration:
            task_types[task_type]["total_time"] += task.duration

    final_results = {
        task.task_id: task.to_dict() for task in all_tasks
    }

    return {
        "final_results": final_results,
        "execution_stats": {
            **state.get("execution_stats", {}),
            "total_tasks_executed": len(all_tasks),
            "successful_tasks": len(successful),
            "failed_tasks": len(failed),
            "success_rate": len(successful) / len(all_tasks) if all_tasks else 0,
            "total_execution_time": total_time,
            "average_task_time": avg_time,
            "max_task_time": max_time,
            "min_task_time": min_time,
            "task_type_stats": task_types,
            "completed_at": datetime.now().isoformat()
        }
    }


def route_execution(state: ConcurrentState) -> str:
    """路由到不同的执行模式"""
    mode = state.get("execution_mode", "sequential")

    routing = {
        "sequential": "execute_sequential",
        "threaded": "execute_threaded",
        "process": "execute_process",
        "async": "execute_async"
    }

    return routing.get(mode, "execute_sequential")


async def execute_async_wrapper(state: ConcurrentState) -> dict:
    """异步执行包装器"""
    return await execute_async(state)


def build_concurrent_graph():
    """构建并发执行图"""
    builder = StateGraph(ConcurrentState)

    # 添加节点
    builder.add_node("create_tasks", create_tasks)
    builder.add_node("execute_sequential", execute_sequential)
    builder.add_node("execute_threaded", execute_threaded)
    builder.add_node("execute_process", execute_process)
    builder.add_node("aggregate_results", aggregate_results)

    # 使用Send处理异步节点
    builder.add_node(
        "execute_async",
        Send("execute_async_wrapper", {"execute_async_wrapper": execute_async_wrapper})
    )

    # 设置边
    builder.add_edge(START, "create_tasks")
    builder.add_conditional_edges("create_tasks", route_execution)

    # 所有执行模式都汇聚到结果聚合
    builder.add_edge("execute_sequential", "aggregate_results")
    builder.add_edge("execute_threaded", "aggregate_results")
    builder.add_edge("execute_process", "aggregate_results")
    builder.add_edge("execute_async", "aggregate_results")
    builder.add_edge("aggregate_results", END)

    return builder.compile()


def demo_sequential_execution():
    """演示顺序执行"""
    print("=" * 60)
    print("演示 1: 顺序执行")
    print("=" * 60)

    app = build_concurrent_graph()

    # 生成Mermaid图
    png_data = app.get_graph().draw_mermaid_png()
    with open("10-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成流程图: 10-graph.png")

    result = app.invoke({
        "task_queue": [],
        "running_tasks": {},
        "completed_tasks": [],
        "failed_tasks": [],
        "max_concurrent": 1,
        "timeout_seconds": 5.0,
        "execution_mode": "sequential",
        "final_results": {},
        "execution_stats": {}
    })

    stats = result["execution_stats"]
    print(f"\n执行统计:")
    print(f"  模式: {stats['mode']}")
    print(f"  总任务数: {stats['total_tasks_executed']}")
    print(f"  成功任务: {stats['successful_tasks']}")
    print(f"  失败任务: {stats['failed_tasks']}")
    print(f"  成功率: {stats['success_rate']:.1%}")
    print(f"  总执行时间: {stats['total_execution_time']:.2f}秒")
    print(f"  平均任务时间: {stats['average_task_time']:.3f}秒")


def demo_threaded_execution():
    """演示线程池并发"""
    print("\n" + "=" * 60)
    print("演示 2: 线程池并发执行")
    print("=" * 60)

    app = build_concurrent_graph()

    result = app.invoke({
        "task_queue": [],
        "running_tasks": {},
        "completed_tasks": [],
        "failed_tasks": [],
        "max_concurrent": 4,
        "timeout_seconds": 5.0,
        "execution_mode": "threaded",
        "final_results": {},
        "execution_stats": {}
    })

    stats = result["execution_stats"]
    print(f"\n执行统计:")
    print(f"  模式: {stats['mode']}")
    print(f"  最大线程数: {stats['max_workers']}")
    print(f"  总任务数: {stats['total_tasks_executed']}")
    print(f"  总执行时间: {stats['total_time']:.2f}秒")
    print(f"  成功率: {stats['success_rate']:.1%}")

    # 显示任务类型统计
    print(f"\n任务类型统计:")
    for task_type, type_stats in stats.get("task_type_stats", {}).items():
        success_rate = type_stats["success"] / type_stats["total"] if type_stats["total"] > 0 else 0
        avg_time = type_stats["total_time"] / type_stats["total"] if type_stats["total"] > 0 else 0
        print(f"  {task_type}: {type_stats['total']}任务, 成功率{success_rate:.1%}, 平均时间{avg_time:.3f}秒")


def demo_process_execution():
    """演示进程池并发"""
    print("\n" + "=" * 60)
    print("演示 3: 进程池并发执行")
    print("=" * 60)
    print("注意: 进程池适合CPU密集型任务")

    app = build_concurrent_graph()

    result = app.invoke({
        "task_queue": [],
        "running_tasks": {},
        "completed_tasks": [],
        "failed_tasks": [],
        "max_concurrent": 2,
        "timeout_seconds": 10.0,
        "execution_mode": "process",
        "final_results": {},
        "execution_stats": {}
    })

    stats = result["execution_stats"]
    print(f"\n执行统计:")
    print(f"  模式: {stats['mode']}")
    print(f"  最大进程数: {stats['max_workers']}")
    print(f"  执行任务数: {stats['total_tasks_executed']}")
    print(f"  剩余任务: {len(result['task_queue'])}")
    print(f"  成功率: {stats['success_rate']:.1%}")


async def demo_async_execution():
    """演示异步并发"""
    print("\n" + "=" * 60)
    print("演示 4: 异步并发执行")
    print("=" * 60)

    app = build_concurrent_graph()

    # 注意: 异步执行需要特殊处理
    print("异步执行演示需要特殊处理，这里展示概念")
    print("实际使用时应使用异步上下文")

    # 创建模拟的异步结果
    stats = {
        "mode": "async",
        "total_tasks_executed": 10,
        "successful_tasks": 9,
        "failed_tasks": 1,
        "success_rate": 0.9,
        "total_time": 1.5,
        "average_task_time": 0.15
    }

    print(f"\n模拟异步执行统计:")
    print(f"  模式: {stats['mode']}")
    print(f"  总任务数: {stats['total_tasks_executed']}")
    print(f"  成功率: {stats['success_rate']:.1%}")
    print(f"  总执行时间: {stats['total_time']:.2f}秒")
    print(f"  平均任务时间: {stats['average_task_time']:.3f}秒")


def demo_performance_comparison():
    """演示性能对比"""
    print("\n" + "=" * 60)
    print("演示 5: 不同执行模式性能对比")
    print("=" * 60)

    modes = ["sequential", "threaded"]
    results = []

    for mode in modes:
        print(f"\n测试模式: {mode}")
        start_time = time.time()

        app = build_concurrent_graph()
        result = app.invoke({
            "task_queue": [],
            "running_tasks": {},
            "completed_tasks": [],
            "failed_tasks": [],
            "max_concurrent": 4 if mode == "threaded" else 1,
            "timeout_seconds": 10.0,
            "execution_mode": mode,
            "final_results": {},
            "execution_stats": {}
        })

        end_time = time.time()
        duration = end_time - start_time

        stats = result["execution_stats"]
        results.append({
            "mode": mode,
            "duration": duration,
            "tasks": stats["total_tasks_executed"],
            "success_rate": stats["success_rate"],
            "avg_time": stats["average_task_time"]
        })

        print(f"  实际耗时: {duration:.2f}秒")
        print(f"  任务统计耗时: {stats['total_execution_time']:.2f}秒")
        print(f"  加速比: {stats['total_execution_time']/duration:.2f}x")

    print("\n" + "-" * 40)
    print("性能对比总结:")
    for r in results:
        print(f"  {r['mode']}: {r['duration']:.2f}秒, {r['tasks']}任务, 成功率{r['success_rate']:.1%}")


def demo_dynamic_concurrency():
    """演示动态并发控制"""
    print("\n" + "=" * 60)
    print("演示 6: 动态并发控制")
    print("=" * 60)

    app = build_concurrent_graph()

    concurrency_levels = [1, 2, 4, 8]
    performance_data = []

    for level in concurrency_levels:
        print(f"\n测试并发数: {level}")

        result = app.invoke({
            "task_queue": [],
            "running_tasks": {},
            "completed_tasks": [],
            "failed_tasks": [],
            "max_concurrent": level,
            "timeout_seconds": 5.0,
            "execution_mode": "threaded",
            "final_results": {},
            "execution_stats": {}
        })

        stats = result["execution_stats"]
        performance_data.append({
            "concurrency": level,
            "total_time": stats["total_time"],
            "success_rate": stats["success_rate"],
            "efficiency": stats["successful_tasks"] / (level * stats["total_time"]) if stats["total_time"] > 0 else 0
        })

        print(f"  总时间: {stats['total_time']:.2f}秒")
        print(f"  成功率: {stats['success_rate']:.1%}")
        print(f"  效率: {performance_data[-1]['efficiency']:.3f} 任务/秒/线程")

    print("\n" + "-" * 40)
    print("最优并发数分析:")
    best = max(performance_data, key=lambda x: x["efficiency"])
    print(f"  推荐并发数: {best['concurrency']} (效率: {best['efficiency']:.3f} 任务/秒/线程)")


if __name__ == "__main__":
    print("LangGraph 并发执行示例 ★★★★")
    print("演示顺序执行、线程池、进程池、异步并发和性能优化")
    print()

    # 演示1: 顺序执行
    demo_sequential_execution()

    # 演示2: 线程池并发
    demo_threaded_execution()

    # 演示3: 进程池并发
    demo_process_execution()

    # 演示4: 异步并发
    import asyncio
    asyncio.run(demo_async_execution())

    # 演示5: 性能对比
    demo_performance_comparison()

    # 演示6: 动态并发控制
    demo_dynamic_concurrency()

    print("\n" + "=" * 60)
    print("关键概念总结:")
    print("1. 顺序执行: 简单可靠，适合任务依赖性强的情况")
    print("2. 线程池: I/O密集型任务，共享内存，需要注意线程安全")
    print("3. 进程池: CPU密集型任务，进程隔离，开销较大")
    print("4. 异步并发: 高并发I/O操作，需要异步编程模型")
    print("5. 动态并发: 根据任务类型和资源调整并发度")
    print("6. 性能监控: 收集执行统计，优化并发策略")
    print("=" * 60)

    print("\n实际应用场景:")
    print("• 批量数据处理: 线程池处理文件I/O")
    print("• 模型推理: 进程池利用多核CPU")
    print("• API调用: 异步并发处理网络请求")
    print("• 数据抓取: 混合并发模式")
    print("• 实时计算: 动态调整并发度")