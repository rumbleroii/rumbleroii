"""Anthropic SDK: change one import."""

from clibridge import Anthropic  # instead of: from anthropic import Anthropic

client = Anthropic()

with client.messages.stream(
    model="claude-sonnet",  # any Claude name works: it's mapped to opus / sonnet / haiku
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a limerick about debugging."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
print()
