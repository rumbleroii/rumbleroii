"""Plain LiteLLM code."""

import litellm

reply = litellm.completion(
    model="clibridge",  # the real model comes from CLIBRIDGE_MODEL in your .env
    messages=[{"role": "user", "content": "Give me three fun facts about octopuses."}],
)
print(reply.choices[0].message.content)
