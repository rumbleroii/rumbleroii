"""OpenAI SDK: change one import and it runs on your Claude Code / Codex subscription."""

from clibridge import OpenAI  # instead of: from openai import OpenAI

client = OpenAI()

reply = client.chat.completions.create(
    model="claude-code",  # or "claude-code/opus", "codex", ...
    messages=[{"role": "user", "content": "Explain recursion in one sentence."}],
)
print(reply.choices[0].message.content)

# Streaming works too.
stream = client.chat.completions.create(
    model="claude-code",
    messages=[{"role": "user", "content": "Write a haiku about the terminal."}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
print()
