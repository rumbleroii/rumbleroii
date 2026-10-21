# clibridge

**Use your Claude Code and Codex subscriptions with any AI library. No API keys, no API bill.**

You write normal OpenAI, LangChain, LiteLLM or Anthropic code. clibridge quietly runs it through the
`claude` or `codex` command already on your computer, so it uses your subscription instead of a paid API key.

```
your code  ──►  clibridge  ──►  claude / codex CLI  ──►  your subscription
```

Good for demos, testing and side projects.

---

## Step 1: Have the CLIs ready

You need at least one of these installed **and logged in**:

| CLI | Install | Log in | Check it works |
|---|---|---|---|
| Claude Code | `npm i -g @anthropic-ai/claude-code` | run `claude` once | `claude -p "hi"` |
| Codex | `npm i -g @openai/codex` | `codex login` | `codex exec "hi"` |

## Step 2: Install clibridge

```bash
git clone https://github.com/rumbleroii/rumbleroii.git
cd rumbleroii/clibridge
pip install -e ".[all]"
```

Check everything is wired up:

```bash
clibridge doctor --ping
```

## Step 3: Use it (pick one way)

### Way 1: Don't change your code at all

Start the local server:

```bash
clibridge serve
```

In another terminal, point your code at it and run it as usual:

```bash
export OPENAI_BASE_URL=http://localhost:8787/v1
export OPENAI_API_KEY=anything

python your_script.py
```

Anthropic SDK code works the same way with `ANTHROPIC_BASE_URL=http://localhost:8787` and `ANTHROPIC_API_KEY=anything`.

### Way 2: Change one line

No server needed: clibridge answers inside your Python process.

**OpenAI SDK**

```python
from clibridge import OpenAI          # was: from openai import OpenAI

client = OpenAI()
reply = client.chat.completions.create(
    model="claude-code",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(reply.choices[0].message.content)
```

**LangChain / LangGraph**

```python
from clibridge.langchain import ChatClaudeCode, ChatCodex

llm = ChatClaudeCode()                # or ChatClaudeCode(model="opus"), ChatCodex()
print(llm.invoke("Hello!").content)
```

**LiteLLM**

```python
import litellm
import clibridge.litellm

clibridge.litellm.register()
litellm.completion(model="claude-code/sonnet", messages=[{"role": "user", "content": "Hello!"}])
```

**Anthropic SDK**

```python
from clibridge import Anthropic       # was: from anthropic import Anthropic
```

**OpenAI Agents SDK**

```python
from agents import Agent, OpenAIResponsesModel, set_tracing_disabled
from clibridge import AsyncOpenAI

set_tracing_disabled(True)
agent = Agent(name="Helper", model=OpenAIResponsesModel(model="claude-code", openai_client=AsyncOpenAI()))
```

More complete versions are in the [`examples/`](examples) folder.

---

## Which model name do I use?

| You write | What runs |
|---|---|
| `claude-code` | Claude Code, its default model |
| `claude-code/opus` (also `sonnet`, `haiku`, `fable`) | Claude Code with that model |
| `codex` | Codex, its default model |
| `codex/gpt-5-codex` (any Codex model) | Codex with that model |
| `claude-code-agent`, `codex-agent` | Agent mode (see below) |

Already have names like `gpt-4o` or `claude-3-5-sonnet` in your code? They work too: `gpt-*` goes to Codex and
`claude-*` goes to Claude Code.

## What works

- ✅ Chat and streaming
- ✅ Tool / function calling (so agents work)
- ✅ Structured output: JSON mode, JSON schema, Pydantic `.parse()` / `with_structured_output`
- ✅ Images
- ✅ Sync and async
- ✅ OpenAI Chat Completions, OpenAI Responses and Anthropic Messages formats

Ignored: `temperature`, `max_tokens`, `top_p`, `n`, `seed`, `logprobs`. The CLIs don't expose them.
Not available: embeddings, audio, image generation.

## Agent mode (optional)

By default the CLI acts as a **plain AI model**: no tools, run from an empty folder.

Use `claude-code-agent` or `codex-agent` as the model to let the CLI work like a coding agent **inside a folder**,
using its own tools to read files, search and run commands. It's read-only unless you allow more:

```bash
clibridge serve --workdir ~/my-project                                  # read-only
clibridge serve --workdir ~/my-project --permission-mode acceptEdits    # Claude may edit files
clibridge serve --workdir ~/my-project --sandbox workspace-write        # Codex may edit files
```

## Handy commands

```bash
clibridge ask "What is a monad?"              # quick test from the terminal
clibridge ask -m codex "Write a regex for emails"
clibridge doctor --ping                       # are the CLIs installed and logged in?
clibridge serve --help                        # all server options
```

## How it works (short version)

1. Your request (messages, tools, schema) is turned into a prompt.
2. clibridge runs `claude -p ...` or `codex exec --json ...` and reads its JSON output.
3. The answer is turned back into the exact format your library expects.

For tool calling, the model is asked to reply in a fixed JSON shape (enforced with the CLI's `--json-schema` /
`--output-schema`), which clibridge converts into real tool calls.

## Good to know

- **It's for demos and testing.** Each call starts a CLI process, which adds a few seconds.
- **It uses your plan's limits.** Every call counts against your Claude / ChatGPT usage, and your plan's terms still apply.
- **Your subscription login is used, not API keys.** `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are removed from the
  CLI's environment so it can't fall back to paid keys (`--keep-env` turns this off).
- **At most 4 calls run at once** by default (`--max-concurrency`).
- **The server listens on localhost only.** Use `--api-key` if you expose it anywhere else.

## Troubleshooting

| You see | Fix |
|---|---|
| `Could not find the claude CLI` | Install it, or set `CLIBRIDGE_CLAUDE_BIN=/path/to/claude` |
| `Invalid API key · Please run /login` | Run `claude` and log in |
| `codex: ... usage limit` | You hit your plan's limit; wait for it to reset |
| LangChain `ChatOpenAI(model="codex")` errors | Use `ChatCodex()`, or pass `use_responses_api=False` |
| LiteLLM rejects `reasoning_effort` | Add `allowed_openai_params=["reasoning_effort"]` |

## Running the tests

The tests use small fake `claude` / `codex` scripts, so they don't need a login and don't use your quota.

```bash
pip install -e ".[dev]"
pytest
```
