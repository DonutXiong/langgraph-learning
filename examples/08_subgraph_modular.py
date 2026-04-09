from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


# ==================== 子图1: 数据预处理 ====================
class PreprocessState(TypedDict):
    """数据预处理状态"""
    raw_data: str
    cleaned_data: str
    preprocessing_steps: Annotated[list[str], operator.add]


def remove_noise(state: PreprocessState) -> dict:
    """去除噪声"""
    cleaned = state["raw_data"].replace("[噪声]", "").strip()
    return {
        "cleaned_data": cleaned,
        "preprocessing_steps": ["噪声去除完成"]
    }


def normalize_text(state: PreprocessState) -> dict:
    """文本标准化"""
    normalized = state["cleaned_data"].lower()
    return {
        "cleaned_data": normalized,
        "preprocessing_steps": ["文本标准化完成"]
    }


def validate_data(state: PreprocessState) -> dict:
    """数据验证"""
    if not state["cleaned_data"]:
        return {"preprocessing_steps": ["数据验证失败: 空数据"]}
    return {"preprocessing_steps": ["数据验证通过"]}


def build_preprocess_subgraph() -> StateGraph:
    """构建数据预处理子图"""
    builder = StateGraph(PreprocessState)

    builder.add_node("remove_noise", remove_noise)
    builder.add_node("normalize_text", normalize_text)
    builder.add_node("validate_data", validate_data)

    builder.add_edge(START, "remove_noise")
    builder.add_edge("remove_noise", "normalize_text")
    builder.add_edge("normalize_text", "validate_data")
    builder.add_edge("validate_data", END)

    return builder.compile()


# ==================== 子图2: 数据分析 ====================
class AnalysisState(TypedDict):
    """数据分析状态"""
    input_data: str
    analysis_results: Annotated[list[str], operator.add]
    metrics: dict


def calculate_statistics(state: AnalysisState) -> dict:
    """计算统计信息"""
    text = state["input_data"]
    word_count = len(text.split())
    char_count = len(text)

    return {
        "analysis_results": [f"统计计算完成: {word_count} 词, {char_count} 字符"],
        "metrics": {"word_count": word_count, "char_count": char_count}
    }


def extract_keywords(state: AnalysisState) -> dict:
    """提取关键词（简化版）"""
    words = state["input_data"].split()[:3]  # 取前3个词作为关键词
    keywords = [w for w in words if len(w) > 2]

    return {
        "analysis_results": [f"关键词提取: {', '.join(keywords)}"],
        "metrics": {"keywords": keywords}
    }


def generate_summary(state: AnalysisState) -> dict:
    """生成摘要（简化版）"""
    text = state["input_data"]
    if len(text) > 50:
        summary = text[:50] + "..."
    else:
        summary = text

    return {
        "analysis_results": [f"摘要生成: {summary}"],
        "metrics": {"summary": summary}
    }


def build_analysis_subgraph() -> StateGraph:
    """构建数据分析子图"""
    builder = StateGraph(AnalysisState)

    builder.add_node("calculate_statistics", calculate_statistics)
    builder.add_node("extract_keywords", extract_keywords)
    builder.add_node("generate_summary", generate_summary)

    builder.add_edge(START, "calculate_statistics")
    builder.add_edge("calculate_statistics", "extract_keywords")
    builder.add_edge("extract_keywords", "generate_summary")
    builder.add_edge("generate_summary", END)

    return builder.compile()


# ==================== 子图3: 报告生成 ====================
class ReportState(TypedDict):
    """报告生成状态"""
    analysis_data: dict
    report_sections: Annotated[list[str], operator.add]
    final_report: str


def create_introduction(state: ReportState) -> dict:
    """创建介绍部分"""
    metrics = state["analysis_data"].get("metrics", {})
    return {
        "report_sections": [
            "=== 分析报告 ===\n",
            f"数据统计: {metrics.get('word_count', 0)} 词, {metrics.get('char_count', 0)} 字符\n"
        ]
    }


def add_analysis_details(state: ReportState) -> dict:
    """添加分析详情"""
    metrics = state["analysis_data"].get("metrics", {})
    sections = []

    if "keywords" in metrics:
        sections.append(f"关键词: {', '.join(metrics['keywords'])}\n")

    if "summary" in metrics:
        sections.append(f"摘要: {metrics['summary']}\n")

    return {"report_sections": sections}


def generate_conclusion(state: ReportState) -> dict:
    """生成结论"""
    all_sections = "".join(state["report_sections"])
    conclusion = "=== 报告结束 ===\n感谢使用数据分析系统。"

    return {
        "report_sections": [conclusion],
        "final_report": all_sections + conclusion
    }


def build_report_subgraph() -> StateGraph:
    """构建报告生成子图"""
    builder = StateGraph(ReportState)

    builder.add_node("create_introduction", create_introduction)
    builder.add_node("add_analysis_details", add_analysis_details)
    builder.add_node("generate_conclusion", generate_conclusion)

    builder.add_edge(START, "create_introduction")
    builder.add_edge("create_introduction", "add_analysis_details")
    builder.add_edge("add_analysis_details", "generate_conclusion")
    builder.add_edge("generate_conclusion", END)

    return builder.compile()


# ==================== 主图: 集成所有子图 ====================
class MainProcessingState(TypedDict):
    """主处理状态"""
    input_text: str
    preprocessed_data: str
    analysis_results: dict
    final_output: str
    processing_log: Annotated[list[str], operator.add]


def run_preprocessing(state: MainProcessingState) -> dict:
    """运行预处理子图"""
    preprocess_graph = build_preprocess_subgraph()

    result = preprocess_graph.invoke({
        "raw_data": state["input_text"],
        "cleaned_data": "",
        "preprocessing_steps": []
    })

    return {
        "preprocessed_data": result["cleaned_data"],
        "processing_log": ["预处理完成"] + result["preprocessing_steps"]
    }


def run_analysis(state: MainProcessingState) -> dict:
    """运行分析子图"""
    analysis_graph = build_analysis_subgraph()

    result = analysis_graph.invoke({
        "input_data": state["preprocessed_data"],
        "analysis_results": [],
        "metrics": {}
    })

    return {
        "analysis_results": result,
        "processing_log": ["分析完成"] + result["analysis_results"]
    }


def run_report_generation(state: MainProcessingState) -> dict:
    """运行报告生成子图"""
    report_graph = build_report_subgraph()

    result = report_graph.invoke({
        "analysis_data": state["analysis_results"],
        "report_sections": [],
        "final_report": ""
    })

    return {
        "final_output": result["final_report"],
        "processing_log": ["报告生成完成"]
    }


def build_main_graph() -> StateGraph:
    """构建主图（集成所有子图）"""
    builder = StateGraph(MainProcessingState)

    builder.add_node("run_preprocessing", run_preprocessing)
    builder.add_node("run_analysis", run_analysis)
    builder.add_node("run_report_generation", run_report_generation)

    builder.add_edge(START, "run_preprocessing")
    builder.add_edge("run_preprocessing", "run_analysis")
    builder.add_edge("run_analysis", "run_report_generation")
    builder.add_edge("run_report_generation", END)

    return builder.compile()


# ==================== 演示函数 ====================
def demo_individual_subgraphs():
    """演示独立子图"""
    print("=" * 60)
    print("演示 1: 独立子图运行")
    print("=" * 60)

    # 生成主图
    main_graph = build_main_graph()
    png_data = main_graph.get_graph().draw_mermaid_png()
    with open("8-main-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成主流程图: 8-main-graph.png")

    # 生成子图
    preprocess_graph = build_preprocess_subgraph()
    png_data = preprocess_graph.get_graph().draw_mermaid_png()
    with open("8-preprocess-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成预处理子图: 8-preprocess-graph.png")

    analysis_graph = build_analysis_subgraph()
    png_data = analysis_graph.get_graph().draw_mermaid_png()
    with open("8-analysis-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成分析子图: 8-analysis-graph.png")

    report_graph = build_report_subgraph()
    png_data = report_graph.get_graph().draw_mermaid_png()
    with open("8-report-graph.png", "wb") as f:
        f.write(png_data)
    print("已生成报告子图: 8-report-graph.png")

    # 测试数据
    test_data = "这是[噪声]一些示例文本，用于[噪声]演示子图功能。"

    print(f"测试数据: {test_data}")
    print()

    # 1. 预处理子图
    print("1. 运行预处理子图:")
    preprocess_graph = build_preprocess_subgraph()
    preprocess_result = preprocess_graph.invoke({
        "raw_data": test_data,
        "cleaned_data": "",
        "preprocessing_steps": []
    })
    print(f"   输入: {test_data}")
    print(f"   输出: {preprocess_result['cleaned_data']}")
    print(f"   步骤: {preprocess_result['preprocessing_steps']}")
    print()

    # 2. 分析子图
    print("2. 运行分析子图:")
    analysis_graph = build_analysis_subgraph()
    analysis_result = analysis_graph.invoke({
        "input_data": preprocess_result["cleaned_data"],
        "analysis_results": [],
        "metrics": {}
    })
    print(f"   分析结果: {analysis_result['analysis_results']}")
    print(f"   指标: {analysis_result['metrics']}")
    print()

    # 3. 报告子图
    print("3. 运行报告子图:")
    report_graph = build_report_subgraph()
    report_result = report_graph.invoke({
        "analysis_data": analysis_result,
        "report_sections": [],
        "final_report": ""
    })
    print(f"   最终报告:\n{report_result['final_report']}")


def demo_integrated_main_graph():
    """演示集成主图"""
    print("\n" + "=" * 60)
    print("演示 2: 集成主图运行")
    print("=" * 60)

    main_graph = build_main_graph()

    test_cases = [
        "简单文本分析",
        "带有[噪声]标记的文本[噪声]需要清理",
        "较长的文本用于测试关键词提取和摘要生成功能"
    ]

    for i, test_data in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"输入: {test_data}")
        print("-" * 40)

        result = main_graph.invoke({
            "input_text": test_data,
            "preprocessed_data": "",
            "analysis_results": {},
            "final_output": "",
            "processing_log": []
        })

        print(f"预处理后: {result['preprocessed_data']}")
        print(f"分析指标: {result['analysis_results'].get('metrics', {})}")
        print(f"处理日志: {result['processing_log']}")
        print(f"\n最终输出:\n{result['final_output']}")


def demo_nested_subgraphs():
    """演示嵌套子图"""
    print("\n" + "=" * 60)
    print("演示 3: 嵌套子图")
    print("=" * 60)

    class NestedState(TypedDict):
        """嵌套处理状态"""
        data: str
        level1_results: Annotated[list[str], operator.add]
        level2_results: Annotated[list[str], operator.add]
        level3_results: Annotated[list[str], operator.add]

    def level1_processing(state: NestedState) -> dict:
        """第一级处理"""
        return {
            "level1_results": [f"Level1: 处理 '{state['data'][:10]}...'"],
            "data": state["data"].upper()
        }

    def level2_processing(state: NestedState) -> dict:
        """第二级处理（调用子图）"""
        # 创建内部子图
        class InnerState(TypedDict):
            inner_data: str
            inner_results: Annotated[list[str], operator.add]

        def inner_step1(inner_state: InnerState) -> dict:
            return {"inner_results": [f"Inner1: 处理 '{inner_state['inner_data'][:5]}...'"]}

        def inner_step2(inner_state: InnerState) -> dict:
            return {"inner_results": [f"Inner2: 完成处理"]}

        # 构建内部子图
        inner_builder = StateGraph(InnerState)
        inner_builder.add_node("inner_step1", inner_step1)
        inner_builder.add_node("inner_step2", inner_step2)
        inner_builder.add_edge(START, "inner_step1")
        inner_builder.add_edge("inner_step1", "inner_step2")
        inner_builder.add_edge("inner_step2", END)

        inner_graph = inner_builder.compile()

        # 运行内部子图
        inner_result = inner_graph.invoke({
            "inner_data": state["data"],
            "inner_results": []
        })

        return {
            "level2_results": [f"Level2: 完成内部处理"] + inner_result["inner_results"],
            "data": state["data"].lower()
        }

    def level3_processing(state: NestedState) -> dict:
        """第三级处理"""
        return {
            "level3_results": [f"Level3: 最终处理完成"],
            "data": state["data"].title()
        }

    # 构建嵌套图
    nested_builder = StateGraph(NestedState)
    nested_builder.add_node("level1_processing", level1_processing)
    nested_builder.add_node("level2_processing", level2_processing)
    nested_builder.add_node("level3_processing", level3_processing)

    nested_builder.add_edge(START, "level1_processing")
    nested_builder.add_edge("level1_processing", "level2_processing")
    nested_builder.add_edge("level2_processing", "level3_processing")
    nested_builder.add_edge("level3_processing", END)

    nested_graph = nested_builder.compile()

    print("嵌套子图结构:")
    print("主图 → Level1 → Level2(内部子图) → Level3 → 结束")
    print()

    test_data = "嵌套子图演示文本"
    print(f"测试数据: {test_data}")
    print()

    result = nested_graph.invoke({
        "data": test_data,
        "level1_results": [],
        "level2_results": [],
        "level3_results": []
    })

    print("处理结果:")
    print(f"最终数据: {result['data']}")
    print(f"Level1 结果: {result['level1_results']}")
    print(f"Level2 结果: {result['level2_results']}")
    print(f"Level3 结果: {result['level3_results']}")


def demo_reusable_subgraph():
    """演示可复用于图"""
    print("\n" + "=" * 60)
    print("演示 4: 可复用于图")
    print("=" * 60)

    # 创建一个通用的验证子图
    class ValidationState(TypedDict):
        value: str
        is_valid: bool
        validation_messages: Annotated[list[str], operator.add]

    def validate_not_empty(state: ValidationState) -> dict:
        if not state["value"]:
            return {
                "is_valid": False,
                "validation_messages": ["值不能为空"]
            }
        return {"validation_messages": ["非空检查通过"]}

    def validate_length(state: ValidationState) -> dict:
        if len(state["value"]) < 3:
            return {
                "is_valid": False,
                "validation_messages": ["长度必须至少3个字符"]
            }
        return {"validation_messages": ["长度检查通过"]}

    def build_validation_subgraph() -> StateGraph:
        builder = StateGraph(ValidationState)
        builder.add_node("validate_not_empty", validate_not_empty)
        builder.add_node("validate_length", validate_length)

        builder.add_edge(START, "validate_not_empty")
        builder.add_conditional_edges(
            "validate_not_empty",
            lambda s: "validate_length" if s.get("is_valid", True) else END
        )
        builder.add_edge("validate_length", END)

        return builder.compile()

    # 在主图中多次使用同一个子图
    class MultiValidationState(TypedDict):
        username: str
        password: str
        email: str
        validation_results: Annotated[list[str], operator.add]

    def validate_username(state: MultiValidationState) -> dict:
        validation_graph = build_validation_subgraph()
        result = validation_graph.invoke({
            "value": state["username"],
            "is_valid": True,
            "validation_messages": []
        })

        messages = [f"用户名验证: {msg}" for msg in result["validation_messages"]]
        return {
            "validation_results": messages,
            "username": state["username"] if result.get("is_valid", True) else ""
        }

    def validate_password(state: MultiValidationState) -> dict:
        validation_graph = build_validation_subgraph()
        result = validation_graph.invoke({
            "value": state["password"],
            "is_valid": True,
            "validation_messages": []
        })

        messages = [f"密码验证: {msg}" for msg in result["validation_messages"]]
        return {
            "validation_results": messages,
            "password": state["password"] if result.get("is_valid", True) else ""
        }

    def validate_email(state: MultiValidationState) -> dict:
        # 电子邮件有特殊验证规则
        validation_graph = build_validation_subgraph()
        result = validation_graph.invoke({
            "value": state["email"],
            "is_valid": True,
            "validation_messages": []
        })

        # 额外的电子邮件验证
        messages = [f"邮箱验证: {msg}" for msg in result["validation_messages"]]
        if "@" not in state["email"]:
            messages.append("邮箱验证: 必须包含@符号")

        return {
            "validation_results": messages,
            "email": state["email"] if result.get("is_valid", True) and "@" in state["email"] else ""
        }

    # 构建主图
    builder = StateGraph(MultiValidationState)
    builder.add_node("validate_username", validate_username)
    builder.add_node("validate_password", validate_password)
    builder.add_node("validate_email", validate_email)

    builder.add_edge(START, "validate_username")
    builder.add_edge("validate_username", "validate_password")
    builder.add_edge("validate_password", "validate_email")
    builder.add_edge("validate_email", END)

    main_graph = builder.compile()

    print("用户注册验证流程:")
    print("用户名 → 密码 → 邮箱")
    print()

    test_cases = [
        {"username": "alice", "password": "pass123", "email": "alice@example.com"},
        {"username": "", "password": "12", "email": "invalid"},
        {"username": "bob", "password": "password", "email": "bob@test.com"}
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"  用户名: {test_case['username']}")
        print(f"  密码: {test_case['password']}")
        print(f"  邮箱: {test_case['email']}")

        result = main_graph.invoke({
            "username": test_case["username"],
            "password": test_case["password"],
            "email": test_case["email"],
            "validation_results": []
        })

        print(f"  验证结果:")
        for msg in result["validation_results"]:
            print(f"    - {msg}")

        print(f"  最终值:")
        print(f"    用户名: {result['username'] or '(无效)'}")
        print(f"    密码: {result['password'] or '(无效)'}")
        print(f"    邮箱: {result['email'] or '(无效)'}")


if __name__ == "__main__":
    print("LangGraph 子图与模块化示例 ★★★☆")
    print("演示子图创建、嵌套、复用和集成")
    print()

    # 演示1: 独立子图
    demo_individual_subgraphs()

    # 演示2: 集成主图
    demo_integrated_main_graph()

    # 演示3: 嵌套子图
    demo_nested_subgraphs()

    # 演示4: 可复用于图
    demo_reusable_subgraph()

    print("\n" + "=" * 60)
    print("关键概念总结:")
    print("1. 子图(Subgraph): 独立的、可复用的图组件")
    print("2. 模块化: 将复杂系统分解为简单组件")
    print("3. 嵌套: 子图中可以包含其他子图")
    print("4. 复用: 同一子图可以在不同上下文中使用")
    print("5. 集成: 将多个子图组合成主图")
    print("=" * 60)

    print("\n实际应用场景:")
    print("• 复杂工作流分解为独立模块")
    print("• 团队协作开发不同子图")
    print("• 代码复用和共享组件")
    print("• 系统架构清晰分层")
    print("• 测试和维护更简单")