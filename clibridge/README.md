# clibridge

**Use your Claude Code and Codex subscriptions with any AI library. No API keys, no API bill.**

Install it once, then set the model name to `claude-code` or `codex` in your normal OpenAI, LiteLLM,
LangChain or Anthropic code. That's it.

```python
from openai import OpenAI

client = OpenAI()
reply = client.chat.completions.create(
    model="claude-code",                      # 👈 the only change
    messages=[{"role": "user", "content": "Hello!"}],
)
print(reply.choices[0].message.content)
```

Behind the scenes, clibridge runs the `claude` or `codex` command already on your computer, so the
request uses your subscription instead of a paid API key.

```
your code  ──►  clibridge  ──►  claude / codex CLI  ──►  your subscription
```

Good for demos, testing and side projects.

---

## Setup (once)

**1. Have the CLIs ready.** You need at least one of these installed **and logged in**:

| CLI | Install | Log in |
|---|---|---|
| Claude Code | `npm i -g @anthropic-ai/claude-code` | run `claude` once |
| Codex | `npm i -g @openai/codex` | `codex login` |

**2. Install clibridge** into the same Python environment as your code:

```bash
git clone https://github.com/rumbleroii/rumbleroii.git
cd rumbleroii/clibridge
pip install -e ".[all]"
```

**3. Check it:**

```bash
clibridge doctor --ping
```

Done. You don't need to import clibridge, run a server or set an API key.

---

## Examples

**OpenAI SDK**

```python
from openai import OpenAI

OpenAI().chat.completions.create(model="claude-code", messages=[{"role": "user", "content": "Hi"}])
```

**LiteLLM** (tools built on LiteLLM, like CrewAI or DSPy, should work the same way)

```python
import litellm

litellm.completion(model="claude-code", messages=[{"role": "user", "content": "Hi"}])
```

**LangChain / LangGraph**

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="claude-code")
llm.invoke("Hi")
```

**Anthropic SDK**

```python
from anthropic import Anthropic

Anthropic().messages.create(model="claude-code", max_tokens=1024, messages=[{"role": "user", "content": "Hi"}])
```

**OpenAI Agents SDK**

```python
from agents import Agent, Runner

agent = Agent(name="Helper", model="claude-code")
print(Runner.run_sync(agent, "Hi").final_output)
```

Runnable versions are in the [`examples/`](examples) folder.

---

## Model names

| Model name | What runs |
|---|---|
| `claude-code` | Claude Code, its default model |
| `claude-code/opus` (also `sonnet`, `haiku`, `fable`) | Claude Code with that model |
| `codex` | Codex, its default model |
| `codex/gpt-5-codex` (any Codex model) | Codex with that model |
| `claude-code-agent`, `codex-agent` | Agent mode (see below) |

**Want your own name, like `inhouse`?** Set an alias:

```bash
export CLIBRIDGE_ALIASES="inhouse=claude-code/sonnet,cheap=claude-code/haiku"
```

Now `model="inhouse"` works everywhere.

**Your other models are not affected.** Only the names above are handled by clibridge. `gpt-4o`,
`claude-sonnet-4-5` and every other name still go to the real API, with your real API key, as before.

## What works

- ✅ Chat and streaming
- ✅ Tool / function calling (so agents work)
- ✅ Structured output: JSON mode, JSON schema, Pydantic
- ✅ Images
- ✅ Sync and async

Ignored: `temperature`, `max_tokens`, `top_p`, `n`, `seed`, `logprobs`. The CLIs don't expose them.
Not available: embeddings, audio, image generation.

## Agent mode (optional)

Normally the CLI acts as a **plain AI model**: no tools, run from an empty folder.

With `claude-code-agent` or `codex-agent`, it works like a coding agent **inside a folder**, using its own tools
to read files, search and run commands. It's read-only unless you allow more:

```bash
export CLIBRIDGE_WORKDIR=~/my-project              # folder to work in (default: current folder)
export CLIBRIDGE_PERMISSION_MODE=acceptEdits       # let Claude edit files
export CLIBRIDGE_SANDBOX=workspace-write           # let Codex edit files
```

## Not using Python? Run the server

For JavaScript, curl, or code running on another machine, start an OpenAI- and Anthropic-compatible server:

```bash
clibridge serve
```

Then point any client at it:

```bash
export OPENAI_BASE_URL=http://localhost:8787/v1      # OpenAI-style clients
export ANTHROPIC_BASE_URL=http://localhost:8787      # Anthropic-style clients
export OPENAI_API_KEY=anything                       # any value works
```

## Handy commands

```bash
clibridge ask "What is a monad?"              # quick test from the terminal
clibridge ask -m codex "Write a regex for emails"
clibridge doctor --ping                       # are the CLIs installed and logged in?
clibridge serve --help                        # all server options
```

## How it works (short version)

1. When Python starts, clibridge adds a tiny hook (about 0.3 ms). When you import `openai`, `litellm`, `anthropic`
   or `langchain_openai`, it watches for requests whose model is a clibridge name.
2. Those requests are turned into a prompt, and clibridge runs `claude -p ...` or `codex exec --json ...`.
3. The answer is turned back into the exact format your library expects.

For tool calling, the model is asked to reply in a fixed JSON shape (enforced with the CLI's `--json-schema` /
`--output-schema`), which clibridge converts into real tool calls.

## Good to know

- **It's for demos and testing.** Each call starts a CLI process, which adds a few seconds.
- **It uses your plan's limits.** Every call counts against your Claude / ChatGPT usage, and your plan's terms still apply.
- **Your subscription login is used, not API keys.** `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are kept away from the CLIs
  so they can't fall back to paid keys.
- **At most 4 calls run at once** by default (`CLIBRIDGE_MAX_CONCURRENCY`).
- **To turn the automatic mode off,** set `CLIBRIDGE_AUTOLOAD=0`. You can still opt in explicitly with
  `from clibridge import OpenAI` (also `AsyncOpenAI`, `Anthropic`) or `from clibridge.langchain import ChatClaudeCode`.

## Troubleshooting

| You see | Fix |
|---|---|
| `Missing credentials` / `api_key must be set` | clibridge isn't installed in this Python. Run `clibridge doctor` with the same Python |
| `Could not find the claude CLI` | Install it, or set `CLIBRIDGE_CLAUDE_BIN=/path/to/claude` |
| `Invalid API key · Please run /login` | Run `claude` and log in |
| `codex: ... usage limit` | You hit your plan's limit; wait for it to reset |
| LangChain `ChatOpenAI(model="codex")` returns a list | That's LangChain's Responses API format: use `.text`, or pass `use_responses_api=False` |

## Running the tests

The tests use small fake `claude` / `codex` scripts, so they don't need a login and don't use your quota.

```bash
pip install -e ".[dev]"
pytest
```
