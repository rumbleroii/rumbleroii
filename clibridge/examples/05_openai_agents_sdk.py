"""OpenAI Agents SDK.  pip install openai-agents"""

from agents import Agent, OpenAIResponsesModel, Runner, function_tool, set_tracing_disabled

from clibridge import AsyncOpenAI

set_tracing_disabled(True)  # tracing would try to upload to OpenAI


@function_tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


agent = Agent(
    name="Math helper",
    instructions="Use the add tool for arithmetic.",
    model=OpenAIResponsesModel(model="codex", openai_client=AsyncOpenAI()),  # or model="claude-code"
    tools=[add],
)
print(Runner.run_sync(agent, "What is 1234 + 4321?").final_output)
