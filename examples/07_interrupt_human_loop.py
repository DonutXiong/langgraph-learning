from __future__ import annotations

import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class ApprovalState(TypedDict):
    """审批流程状态"""
    document_name: str
    current_step: str
    approvals: Annotated[list[str], operator.add]
    rejections: Annotated[list[str], operator.add]
    status: str
    requires_human_input: bool


class HumanInputRequired(Exception):
    """需要人工输入的异常"""
    pass


def draft_document(state: ApprovalState) -> dict:
    """起草文档"""
    return {
        "current_step": "draft",
        "approvals": ["文档起草完成"],
        "status": "等待初审",
        "requires_human_input": True  # 需要人工审核
    }


def initial_review(state: ApprovalState) -> dict:
    """初审"""
    # 模拟需要人工决策
    raise interrupt("initial_review_decision")


def make_initial_decision(state: ApprovalState, decision: str) -> dict:
    """做出初审决策"""
    if decision == "approve":
        return {
            "current_step": "initial_approved",
            "approvals": ["初审通过"],
            "status": "等待终审",
            "requires_human_input": True
        }
    else:
        return {
            "current_step": "initial_rejected",
            "rejections": ["初审驳回: " + decision],
            "status": "需要修改",
            "requires_human_input": True
        }


def revise_document(state: ApprovalState) -> dict:
    """修订文档"""
    return {
        "current_step": "revised",
        "approvals": ["文档已修订"],
        "status": "重新提交初审",
        "requires_human_input": False
    }


def final_review(state: ApprovalState) -> dict:
    """终审"""
    # 模拟需要人工决策
    raise interrupt("final_review_decision")


def make_final_decision(state: ApprovalState, decision: str) -> dict:
    """做出终审决策"""
    if decision == "approve":
        return {
            "current_step": "final_approved",
            "approvals": ["终审通过 - 文档已批准"],
            "status": "完成",
            "requires_human_input": False
        }
    else:
        return {
            "current_step": "final_rejected",
            "rejections": ["终审驳回: " + decision],
            "status": "终止",
            "requires_human_input": False
        }


def archive_document(state: ApprovalState) -> dict:
    """归档文档"""
    return {
        "current_step": "archived",
        "approvals": ["文档已归档"],
        "status": "流程结束",
        "requires_human_input": False
    }


def route_after_draft(state: ApprovalState) -> str:
    """起草后的路由"""
    return "initial_review"


def route_after_initial(state: ApprovalState) -> str:
    """初审后的路由"""
    if state["current_step"] == "initial_approved":
        return "final_review"
    elif state["current_step"] == "initial_rejected":
        return "revise_document"
    return END


def route_after_revision(state: ApprovalState) -> str:
    """修订后的路由"""
    return "initial_review"


def route_after_final(state: ApprovalState) -> str:
    """终审后的路由"""
    if state["current_step"] == "final_approved":
        return "archive_document"
    return END


def build_approval_graph():
    """构建审批流程图"""
    builder = StateGraph(ApprovalState)

    # 添加节点
    builder.add_node("draft_document", draft_document)
    builder.add_node("initial_review", initial_review)
    builder.add_node("revise_document", revise_document)
    builder.add_node("final_review", final_review)
    builder.add_node("archive_document", archive_document)

    # 添加边
    builder.add_edge(START, "draft_document")
    builder.add_conditional_edges("draft_document", route_after_draft)
    builder.add_conditional_edges("initial_review", route_after_initial)
    builder.add_conditional_edges("revise_document", route_after_revision)
    builder.add_conditional_edges("final_review", route_after_final)
    builder.add_edge("archive_document", END)

    return builder.compile()


def demo_basic_interrupt():
    """演示基础中断机制"""
    print("=" * 60)
    print("演示 1: 基础中断机制")
    print("=" * 60)

    app = build_approval_graph()

    # 生成Mermaid图
    png_data = app.get_graph().draw_mermaid_png()
    with open("7-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成流程图: 7-graph.png")

    document_name = "项目计划书_v1.0"

    print(f"文档: {document_name}")
    print("\n开始审批流程...")
    print("-" * 40)

    try:
        # 第一步：起草文档
        state = {"document_name": document_name, "approvals": [], "rejections": [], "status": "开始", "requires_human_input": False}
        state = app.invoke(state)
        print(f"1. {state['current_step']}: {state['status']}")
        print(f"   审批记录: {state['approvals'][-1]}")

        # 第二步：尝试初审（会触发中断）
        print("\n2. 进入初审阶段...")
        state = app.invoke(state)
    except interrupt as e:
        print(f"   ⚠️ 流程中断: {e}")
        print("   需要人工决策: 初审是否通过？")

        # 模拟人工决策
        print("   模拟人工输入: 输入 'approve' 或 'reject'")
        decision = "approve"  # 模拟用户输入
        print(f"   决策结果: {decision}")

        # 使用中断处理函数
        if e.value == "initial_review_decision":
            state = app.invoke(state, {"initial_review": make_initial_decision(state, decision)})

        print(f"   继续执行...")
        print(f"   当前状态: {state['status']}")
        print(f"   审批记录: {state['approvals'][-1] if state['approvals'] else '无'}")

    print("-" * 40)
    print("基础中断演示完成")


def demo_full_approval_workflow():
    """演示完整审批工作流"""
    print("\n" + "=" * 60)
    print("演示 2: 完整审批工作流")
    print("=" * 60)

    app = build_approval_graph()
    document_name = "年度预算报告"

    print(f"文档: {document_name}")
    print("\n模拟完整审批流程（包含多次中断）...")
    print("-" * 40)

    # 初始化状态
    state = {
        "document_name": document_name,
        "approvals": [],
        "rejections": [],
        "status": "开始",
        "requires_human_input": False
    }

    step = 1

    def execute_step(step_name: str):
        nonlocal state, step
        try:
            print(f"\n{step}. {step_name}...")
            state = app.invoke(state)
            if "current_step" in state:
                print(f"   ✅ 完成: {state['status']}")
                if state['approvals'] and state['approvals'][-1] not in [s['approvals'][-1] for s in history if 'approvals' in s and s['approvals']]:
                    print(f"   记录: {state['approvals'][-1]}")
            step += 1
            return True
        except interrupt as e:
            print(f"   ⏸️ 中断: {e.value}")
            return False

    def handle_interrupt(interrupt_value: str, decision_func, decision: str):
        nonlocal state
        print(f"   需要人工决策: {interrupt_value}")
        print(f"   模拟决策: {decision}")
        state = app.invoke(state, {interrupt_value: decision_func(state, decision)})
        print(f"   决策结果: {state['status']}")

    history = []

    # 步骤1: 起草
    if execute_step("起草文档"):
        history.append(state.copy())

    # 步骤2: 初审（会中断）
    if not execute_step("初审"):
        handle_interrupt("initial_review_decision", make_initial_decision, "reject")  # 模拟驳回
        history.append(state.copy())

        # 重新初审
        execute_step("重新初审")
        history.append(state.copy())

        if not execute_step("再次初审"):
            handle_interrupt("initial_review_decision", make_initial_decision, "approve")  # 模拟通过
            history.append(state.copy())

    # 步骤3: 终审（会中断）
    if not execute_step("终审"):
        handle_interrupt("final_review_decision", make_final_decision, "approve")  # 模拟通过
        history.append(state.copy())

    # 步骤4: 归档
    execute_step("归档文档")
    history.append(state.copy())

    print("\n" + "-" * 40)
    print("审批流程完成！")
    print(f"最终状态: {state['status']}")
    print(f"总审批记录: {len(state['approvals'])} 条")
    if state['rejections']:
        print(f"驳回记录: {len(state['rejections'])} 条")


def demo_human_in_the_loop():
    """演示Human-in-the-Loop模式"""
    print("\n" + "=" * 60)
    print("演示 3: Human-in-the-Loop 模式")
    print("=" * 60)

    class ContentModerationState(TypedDict):
        """内容审核状态"""
        content: str
        steps: Annotated[list[str], operator.add]
        decisions: Annotated[list[str], operator.add]
        final_decision: str

    def analyze_content(state: ContentModerationState) -> dict:
        """分析内容"""
        return {
            "steps": ["内容分析完成"],
            "decisions": ["自动分析: 需要人工审核"]
        }

    def human_review(state: ContentModerationState) -> dict:
        """人工审核（触发中断）"""
        raise interrupt("human_review_decision")

    def make_human_decision(state: ContentModerationState, decision: str) -> dict:
        """人工决策"""
        return {
            "decisions": [f"人工审核: {decision}"],
            "final_decision": decision
        }

    def publish_content(state: ContentModerationState) -> dict:
        """发布内容"""
        if state["final_decision"] == "approve":
            return {"steps": ["内容已发布"]}
        else:
            return {"steps": ["内容已拒绝"]}

    # 构建图
    builder = StateGraph(ContentModerationState)
    builder.add_node("analyze_content", analyze_content)
    builder.add_node("human_review", human_review)
    builder.add_node("publish_content", publish_content)

    builder.add_edge(START, "analyze_content")
    builder.add_edge("analyze_content", "human_review")
    builder.add_edge("human_review", "publish_content")
    builder.add_edge("publish_content", END)

    app = builder.compile()

    print("场景: 内容审核平台")
    print("流程: 自动分析 → 人工审核 → 发布决策")
    print("-" * 40)

    contents = [
        "这是一篇正常的文章。",
        "这篇文章可能包含敏感内容。",
        "用户生成的评论内容。"
    ]

    for i, content in enumerate(contents, 1):
        print(f"\n审核内容 {i}: {content[:20]}...")

        state = {"content": content, "steps": [], "decisions": [], "final_decision": ""}

        try:
            # 自动分析
            state = app.invoke(state)
            print(f"  1. {state['steps'][-1]}")

            # 人工审核（会中断）
            state = app.invoke(state)
        except interrupt as e:
            print(f"  2. ⏸️ 流程中断，等待人工审核...")

            # 模拟人工审核决策
            import random
            decision = random.choice(["approve", "reject", "modify"])
            print(f"     模拟人工决策: {decision}")

            # 处理中断
            state = app.invoke(state, {"human_review_decision": make_human_decision(state, decision)})

            # 继续执行
            state = app.invoke(state)
            print(f"  3. {state['steps'][-1]}")

        print(f"  最终决策: {state['final_decision']}")
        print(f"  所有决策记录: {state['decisions']}")

    print("-" * 40)
    print("Human-in-the-Loop 模式演示完成")


def demo_error_handling_with_interrupt():
    """演示错误处理与中断结合"""
    print("\n" + "=" * 60)
    print("演示 4: 错误处理与中断结合")
    print("=" * 60)

    class ProcessingState(TypedDict):
        """处理状态"""
        data: str
        steps: Annotated[list[str], operator.add]
        errors: Annotated[list[str], operator.add]
        requires_intervention: bool

    def validate_data(state: ProcessingState) -> dict:
        """验证数据"""
        if "error" in state["data"].lower():
            raise interrupt("validation_error")
        return {"steps": ["数据验证通过"]}

    def handle_validation_error(state: ProcessingState, action: str) -> dict:
        """处理验证错误"""
        if action == "fix":
            fixed_data = state["data"].replace("error", "corrected")
            return {
                "data": fixed_data,
                "steps": ["数据已修复"],
                "requires_intervention": False
            }
        else:
            return {
                "steps": ["数据被拒绝"],
                "errors": ["验证失败: 包含错误内容"],
                "requires_intervention": False
            }

    def process_data(state: ProcessingState) -> dict:
        """处理数据"""
        return {"steps": ["数据处理完成"]}

    # 构建图
    builder = StateGraph(ProcessingState)
    builder.add_node("validate_data", validate_data)
    builder.add_node("process_data", process_data)

    builder.add_edge(START, "validate_data")
    builder.add_conditional_edges("validate_data", lambda s: "process_data" if not s.get("requires_intervention", False) else END)
    builder.add_edge("process_data", END)

    app = builder.compile()

    print("场景: 数据处理流程中的错误恢复")
    print("-" * 40)

    test_cases = [
        {"data": "正常数据", "expected": "成功"},
        {"data": "包含error的数据", "expected": "需要修复"},
        {"data": "另一个错误数据", "expected": "需要修复"}
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test['data']}")

        state = {"data": test["data"], "steps": [], "errors": [], "requires_intervention": False}

        try:
            state = app.invoke(state)
            print(f"  结果: {state['steps'][-1]}")
        except interrupt as e:
            print(f"  中断: {e.value}")

            # 模拟人工干预
            print("  模拟人工干预: 选择 'fix' 或 'reject'")
            action = "fix"  # 模拟选择修复

            state = app.invoke(state, {"validation_error": handle_validation_error(state, action)})
            print(f"  干预结果: {state['steps'][-1]}")

            # 继续处理
            if "requires_intervention" not in state or not state["requires_intervention"]:
                state = app.invoke(state)
                if state["steps"]:
                    print(f"  继续处理: {state['steps'][-1]}")

    print("-" * 40)
    print("错误处理与中断结合演示完成")


if __name__ == "__main__":
    print("LangGraph 中断与人工干预示例 ★★★☆")
    print("演示流程中断、人工决策和Human-in-the-Loop模式")
    print()

    # 演示1: 基础中断机制
    demo_basic_interrupt()

    # 演示2: 完整审批工作流
    demo_full_approval_workflow()

    # 演示3: Human-in-the-Loop模式
    demo_human_in_the_loop()

    # 演示4: 错误处理与中断结合
    demo_error_handling_with_interrupt()

    print("\n" + "=" * 60)
    print("关键概念总结:")
    print("1. interrupt() 函数: 主动触发流程中断")
    print("2. Human-in-the-Loop: 人工参与决策循环")
    print("3. 中断处理: 通过特定函数处理中断")
    print("4. 错误恢复: 中断与错误处理结合")
    print("5. 流程控制: 灵活控制工作流执行")
    print("=" * 60)

    print("\n实际应用场景:")
    print("• 审批流程需要人工决策")
    print("• 内容审核需要人工干预")
    print("• 错误处理需要人工修复")
    print("• 质量控制需要人工检查")
    print("• 敏感操作需要人工确认")