"""
LangGraph agent node functions.

These are the pure functions wired into the StateGraph:
- call_model: invokes the LLM with the current message state
- should_continue: decides whether to route to tools or END
"""

from langgraph.graph import END, MessagesState


def should_continue(state: MessagesState) -> str:
    """Route to 'tools' if the last message has tool calls, otherwise END."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


def call_model(state: MessagesState, model):
    """Invoke the LLM and return the response as a new message."""
    messages = state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}
