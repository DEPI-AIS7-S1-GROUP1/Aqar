"""
LangGraph In-Memory Interrupt & Resume Spike (Part 1)

This script demonstrates:
1. Graph execution using LangGraph
2. Pausing execution using interrupt()
3. Resuming execution using Command(resume=...)
4. Preserving state with InMemorySaver
5. Storing human response in final state
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


# State definition
class AgentState(TypedDict):
    """Simple state containing the question and human response."""
    question: str
    human_response: str | None


def process_request(state: AgentState) -> AgentState:
    """
    Node 1: Process the initial request.
    
    Simulates assistant's initial processing by reading and printing
    the user's question. No LLM or external service required.
    """
    print(f"\n[Node 1: process_request] Processing question: {state['question']}")
    
    # Return state unchanged - no updates needed at this stage
    return state


def human_review(state: AgentState) -> AgentState:
    """
    Node 2: Request human review and store response.
    
    Calls interrupt() to pause execution and request human input.
    After resumption, stores the human response in state.
    
    Important: This node restarts from the beginning when resumed,
    so we don't perform side effects before calling interrupt().
    """
    print("\n[Node 2: human_review] Requesting human intervention...")
    
    # Prepare interrupt payload with context
    interrupt_payload = {
        "message": "Human intervention required",
        "original_question": state["question"],
        "expected_response": "Approval or rejection decision from broker"
    }
    
    # Call interrupt() to pause execution
    # The return value will be the resume value provided when resuming
    human_input = interrupt(interrupt_payload)
    
    # Code after interrupt() runs only after resumption
    print(f"\n[Node 2: human_review] Received human response: {human_input}")
    
    # Store human response in state
    return {
        "question": state["question"],
        "human_response": human_input
    }


def build_graph() -> StateGraph:
    """
    Build the LangGraph workflow with in-memory checkpointing.
    
    Flow: START -> process_request -> human_review -> END
    """
    # Create graph with state schema
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("process_request", process_request)
    workflow.add_node("human_review", human_review)
    
    # Define edges
    workflow.add_edge(START, "process_request")
    workflow.add_edge("process_request", "human_review")
    workflow.add_edge("human_review", END)
    
    # Compile with in-memory checkpointer
    checkpointer = InMemorySaver()
    return workflow.compile(checkpointer=checkpointer)


def run_experiment():
    """
    Execute the complete interrupt and resume experiment.
    
    Uses a stable thread_id to maintain state across invocations.
    """
    print("=" * 70)
    print("LangGraph In-Memory Interrupt & Resume Experiment")
    print("=" * 70)
    
    # Build the graph
    graph = build_graph()
    
    # Use stable thread ID for state persistence
    thread_id = "s0-t5-1-memory-test"
    config = {"configurable": {"thread_id": thread_id}}
    
    # Initial state
    initial_state = {"question": "I need help with my booking"}
    
    print("\n" + "=" * 70)
    print("PHASE 1: First Invocation (should trigger interrupt)")
    print("=" * 70)
    
    # First invocation - should pause at interrupt
    result = graph.invoke(initial_state, config)
    
    print("\n[RESULT] First invocation complete")
    print(f"[RESULT] Execution paused: {'__interrupt__' in result}")
    
    # Check if interrupt occurred
    if "__interrupt__" not in result:
        raise RuntimeError("FAILED: First invocation did not produce an interrupt")
    
    interrupt_data = result["__interrupt__"]
    print(f"[RESULT] Interrupt payload: {interrupt_data}")
    
    # Verify interrupt payload contains the question
    if len(interrupt_data) == 0:
        raise RuntimeError("FAILED: Interrupt payload is empty")
    
    # Get the first interrupt payload (there should be only one)
    first_interrupt = interrupt_data[0]
    payload = first_interrupt.value
    
    if payload.get("original_question") != initial_state["question"]:
        raise RuntimeError("FAILED: Interrupt payload does not contain original question")
    
    print("[CHECK] Interrupt triggered successfully")
    print("[CHECK] Interrupt payload contains original question")
    
    print("\n" + "=" * 70)
    print("PHASE 2: Resume Invocation (with human response)")
    print("=" * 70)
    
    # Resume execution with human response
    human_response = "Broker approved the request"
    resume_command = Command(resume=human_response)
    
    print(f"\n[RESUME] Resuming with: {human_response}")
    
    # Second invocation - resume from interrupt
    final_result = graph.invoke(resume_command, config)
    
    print("\n[RESULT] Resume invocation complete")
    print(f"[RESULT] Final state: {final_result}")
    
    # Verify final state
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    checks = []
    
    # Check 1: First invocation produced an interrupt
    checks.append(("First invocation produced interrupt", "__interrupt__" in result))
    
    # Check 2: Interrupt payload contains original question
    checks.append(("Interrupt payload contains original question", 
                   payload.get("original_question") == initial_state["question"]))
    
    # Check 3: Second invocation completed without exception
    checks.append(("Second invocation completed", final_result is not None))
    
    # Check 4: Final state contains original question
    checks.append(("Final state contains original question", 
                   final_result.get("question") == initial_state["question"]))
    
    # Check 5: Final state contains exact human response
    checks.append(("Final state contains human response", 
                   final_result.get("human_response") == human_response))
    
    # Check 6: Execution reached END (no interrupt in final result)
    checks.append(("Execution reached END", "__interrupt__" not in final_result))
    
    # Print verification results
    all_passed = True
    for check_name, passed in checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("ALL VERIFICATION CHECKS PASSED")
        print("Part 1: In-Memory Interrupt & Resume - SUCCESS")
    else:
        raise RuntimeError("FAILED: One or more verification checks failed")
    
    print("=" * 70)
    
    return final_result


if __name__ == "__main__":
    try:
        result = run_experiment()
        print("\n[SUCCESS] Experiment completed successfully")
        print(f"\nFinal state:\n  question: {result['question']}\n  human_response: {result['human_response']}")
    except Exception as e:
        print(f"\n[ERROR] Experiment failed: {e}")
        raise
