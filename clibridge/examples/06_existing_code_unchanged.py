"""Existing code, not changed at all. Run the server, set two env vars, done.

    clibridge serve                                  # terminal 1
    export OPENAI_BASE_URL=http://localhost:8787/v1  # terminal 2
    export OPENAI_API_KEY=anything
    python examples/06_existing_code_unchanged.py
"""

from openai import OpenAI

client = OpenAI()
reply = client.chat.completions.create(
    model="gpt-4o-mini",  # gpt-* names go to Codex; use "claude-code" for Claude
    messages=[{"role": "user", "content": "Say hello!"}],
)
print(reply.choices[0].message.content)
