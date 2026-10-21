"""LiteLLM: register the providers once, then use "claude-code/<model>" or "codex/<model>"."""

import litellm

import clibridge.litellm

clibridge.litellm.register()

reply = litellm.completion(
    model="claude-code/sonnet",  # or "codex/default", "claude-code/default", ...
    messages=[{"role": "user", "content": "Give me three fun facts about octopuses."}],
)
print(reply.choices[0].message.content)
