"""Agent mode: Claude Code works inside a folder with its own tools (read files, run commands...)."""

from clibridge import BridgeConfig, OpenAI

# Read-only by default. Add permission_mode="acceptEdits" to let it edit files.
client = OpenAI(config=BridgeConfig(workdir="."))

reply = client.chat.completions.create(
    model="claude-code-agent",  # or "codex-agent"
    messages=[{"role": "user", "content": "Look at the files here and summarize this project in 3 bullets."}],
)
print(reply.choices[0].message.content)
