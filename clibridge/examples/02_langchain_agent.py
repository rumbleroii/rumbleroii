"""LangChain + LangGraph agent with a tool.  pip install langgraph"""

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from clibridge.langchain import ChatClaudeCode  # or ChatCodex


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"It's 21C and sunny in {city}."


agent = create_react_agent(ChatClaudeCode(model="sonnet"), [get_weather])
result = agent.invoke({"messages": [("user", "What's the weather in Lisbon?")]})
print(result["messages"][-1].content)
