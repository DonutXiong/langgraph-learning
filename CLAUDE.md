# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Chinese-language learning project for LangGraph, focused on practical examples rather than feature accumulation. The project demonstrates core LangGraph concepts through small, runnable examples.

## Key Dependencies

- `langgraph>=1.0.10` - Core workflow orchestration
- `langchain>=1.0.0` - LLM framework integration  
- `langchain-openai>=1.0.0` - OpenAI model support
- `python-dotenv>=1.0.1` - Environment variable management

## Development Setup

1. Create virtual environment: `python3 -m venv .venv`
2. Activate: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix)
3. Install dependencies: `python3 -m pip install -r requirements.txt`
4. Copy environment template: `cp .env.example .env`
5. Configure API keys in `.env` for LLM examples (optional for basic examples)

## Running Examples

The project follows a recommended learning sequence with three difficulty levels:

### Level 1: Foundation (01-04)
1. **Basic StateGraph** - `python examples/01_basic_state_graph.py`
   - Demonstrates START → Node → Node → END flow
   - Shows how nodes return partial state updates
   - Uses `Annotated[list[str], operator.add]` for list field merging

2. **Conditional Loop** - `python examples/02_conditional_loop.py`
   - Shows `add_conditional_edges` for branching logic
   - Implements loop until condition met (score ≥ 80)
   - Demonstrates state-based routing decisions

3. **Functional API Workflow** - `python examples/04_functional_api_workflow.py`
   - Uses `@entrypoint` and `@task` decorators
   - Shows alternative to explicit graph building
   - Demonstrates concurrent task execution with `.result()` waiting

4. **Tool Calling Agent** - `python examples/03_tool_calling_agent.py`
   - Requires `.env` configuration with API keys
   - Shows `messages` state with `operator.add` reducer
   - Implements model → tools → model loop
   - Uses `bind_tools()` for tool-aware LLM calls

### Level 2: Intermediate Features (05-08) ★★☆☆ ~ ★★★☆
5. **Checkpoint & Memory** - `python examples/05_checkpoint_memory.py`
   - Demonstrates `MemorySaver` and `FileSystemCheckpointer`
   - Shows state persistence and recovery
   - Implements multi-session support

6. **Stream Output** - `python examples/06_stream_output.py`
   - Shows `stream()` method for real-time output
   - Demonstrates progress display and callbacks
   - Compares different streaming modes

7. **Interrupt & Human Loop** - `python examples/07_interrupt_human_loop.py`
   - Demonstrates `interrupt()` mechanism
   - Implements Human-in-the-Loop patterns
   - Shows error handling with human intervention

8. **Subgraph & Modularity** - `python examples/08_subgraph_modular.py`
   - Shows subgraph creation and nesting
   - Demonstrates code reuse and modular design
   - Implements complex system decomposition

### Level 3: Advanced Applications (09-12) ★★★☆ ~ ★★★★
9. **Workflow Orchestration** - `python examples/09_workflow_orchestration.py`
   - Demonstrates complex multi-step workflows
   - Shows conditional routing and error recovery
   - Integrates checkpoints for persistence

10. **Concurrent Nodes** - `python examples/10_concurrent_nodes.py`
    - Shows sequential, threaded, and process-based execution
    - Demonstrates async concurrency patterns
    - Implements performance monitoring and optimization

11. **Error Recovery** - `python examples/11_error_recovery.py`
    - Demonstrates error detection and classification
    - Shows multiple recovery strategies (retry, fallback, degrade, escalate, abort)
    - Implements monitoring metrics and alerts

12. **Tracing & Monitoring** - `python examples/12_langsmith_tracing.py`
    - Demonstrates trace sessions and event recording
    - Shows performance analysis and debugging
    - Implements production-ready monitoring configuration

## Code Architecture

### State Definitions
All examples use `TypedDict` for state definition with `Annotated` fields for reducers:
- `Annotated[list[str], operator.add]` for accumulating lists
- `Annotated[list[AnyMessage], operator.add]` for chat message history
- Advanced examples use custom data classes and enums for complex state

### Graph Building Pattern
1. Define state type as `TypedDict` or use `StateGraph` with state schema
2. Create `StateGraph` instance with state type (optionally with checkpointer)
3. Add nodes with `add_node(name, function)`
4. Connect edges with `add_edge(source, target)` or `add_conditional_edges(source, routing_function)`
5. Compile with `compile()`

### Advanced Patterns
- **Checkpointing**: Use `MemorySaver` or `FileSystemCheckpointer` for state persistence
- **Interrupts**: Use `interrupt()` for human-in-the-loop workflows
- **Subgraphs**: Create reusable graph components with nested execution
- **Concurrency**: Implement parallel execution with thread/process pools
- **Error Recovery**: Design resilient systems with multiple recovery strategies
- **Tracing**: Implement monitoring and debugging with trace events

### Node Functions
- Accept state dictionary as parameter
- Return partial state updates as dictionary
- Can access any field from incoming state
- Advanced nodes may raise `interrupt` or handle errors

### Environment Configuration
- Default model: DeepSeek (`openai:deepseek-chat`)
- API key configuration in `.env` file
- Base URL for OpenAI-compatible APIs (e.g., DeepSeek)
- Optional LangSmith tracing support (simulated in examples)

## Common Development Tasks

### Adding New Examples
1. Create new file in `examples/` directory with appropriate difficulty level (★☆☆☆ ~ ★★★★)
2. Follow existing patterns for state definition and graph building
3. Include comprehensive demonstrations with clear console output
4. Add `if __name__ == "__main__":` block for direct execution
5. Update `main.py` `EXAMPLES` list and relevant documentation

### Extending Existing Examples
- Add new fields to state `TypedDict` or use data classes for complex state
- Create new node functions that return partial updates
- Implement advanced features like error handling, concurrency, or tracing
- Connect nodes with appropriate edges or conditional routing
- Test with `app.invoke(initial_state)` and verify error cases

### Adding Tools to Agent
1. Define tool with `@tool` decorator
2. Add to `TOOLS` list in `03_tool_calling_agent.py`
3. Update `TOOLS_BY_NAME` mapping
4. The model will automatically learn to use new tools via `bind_tools()`

### Implementing Advanced Features
1. **Checkpointing**: Add `checkpointer` parameter to `StateGraph` constructor
2. **Interrupts**: Use `interrupt()` and handle with specific functions
3. **Subgraphs**: Create reusable graphs and integrate into main workflow
4. **Concurrency**: Use appropriate execution mode based on task type
5. **Error Recovery**: Implement multiple recovery strategies with monitoring
6. **Tracing**: Add trace events and session management

## Project Structure

- `examples/` - Learning examples in three difficulty levels
  - `01-04_basic/` - Foundation concepts
  - `05-08_intermediate/` - Advanced features
  - `09-12_advanced/` - Complex applications
- `docs/learning-path.md` - Detailed learning roadmap with difficulty ratings
- `main.py` - Project overview and categorized example listing
- `.env.example` - Template for environment configuration
- `requirements.txt` - Python dependencies
- `traces/` - Generated trace data from LangSmith examples (auto-created)

## Notes for Future Development

- Examples are designed to be minimal and focused on single concepts
- Chinese comments and prompts are intentional for target audience
- Difficulty ratings (★☆☆☆ ~ ★★★★) help users choose appropriate learning path
- The `02_conditional_loop.py` example simulates learning progression with increasing scores
- Functional API (`04_functional_api_workflow.py`) provides alternative to explicit graph construction
- Agent example (`03_tool_calling_agent.py`) requires API keys but follows official patterns
- Advanced examples demonstrate production-ready patterns and best practices
- Tracing example (`12_langsmith_tracing.py`) uses mock client; real usage requires LangSmith setup