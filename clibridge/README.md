# clibridge

**Use your Claude Code and Codex subscriptions with any AI library. No API keys, no API bill.**

Write normal OpenAI, LiteLLM, LangChain or Anthropic code and set the model to `clibridge`.
A `.env` file decides which real model that is.

```python
from openai import OpenAI

client = OpenAI()
reply = client.chat.completions.create(
    model="clibridge",                        # 👈 the only change
    messages=[{"role": "user", "content": "Hello!"}],
)
print(reply.choices[0].message.content)
```

```bash
# .env
CLIBRIDGE_MODEL=claude-code/sonnet
```

Behind the scenes, clibridge runs the `claude` or `codex` command already on your computer, so the request
uses your subscription instead of a paid API key.

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

**3. Add a `.env` file** to your project folder (copy [`examples/.env.example`](examples/.env.example)):

```bash
CLIBRIDGE_MODEL=claude-code/sonnet     # which model "clibridge" means
CLIBRIDGE_EFFORT=high                  # optional: how hard it thinks
```

**4. Check it:**

```bash
clibridge doctor --ping
```

Done. You don't need to import clibridge, run a server or set an API key.

---

## Examples

Every example uses `model="clibridge"`. Change the model in `.env`, not in your code.

**OpenAI SDK**

```python
from openai import OpenAI

OpenAI().chat.completions.create(model="clibridge", messages=[{"role": "user", "content": "Hi"}])
```

**LiteLLM** (tools built on LiteLLM, like CrewAI or DSPy, should work the same way)

```python
import litellm

litellm.completion(model="clibridge", messages=[{"role": "user", "content": "Hi"}])
```

**LangChain / LangGraph**

```python
from langchain_openai import ChatOpenAI

ChatOpenAI(model="clibridge").invoke("Hi")
```

**Anthropic SDK**

```python
from anthropic import Anthropic

Anthropic().messages.create(model="clibridge", max_tokens=1024, messages=[{"role": "user", "content": "Hi"}])
```

**OpenAI Agents SDK**

```python
from agents import Agent, Runner

agent = Agent(name="Helper", model="clibridge")
print(Runner.run_sync(agent, "Hi").final_output)
```

Runnable versions are in the [`examples/`](examples) folder.

---

## Supported models

Put any of these in `CLIBRIDGE_MODEL`, or use them directly as the model name in your code.

### Claude (needs Claude Code)

| Model name | What runs |
|---|---|
| `claude-code` | Your Claude Code default model |
| `claude-code/fable` | Latest Fable |
| `claude-code/opus` | Latest Opus |
| `claude-code/sonnet` | Latest Sonnet |
| `claude-code/haiku` | Latest Haiku (fastest) |
| `claude-code/<model id>` | A specific version, e.g. `claude-code/claude-opus-5-5`, `claude-code/claude-sonnet-5-5`, `claude-code/claude-haiku-5-5`, `claude-code/claude-fable-5-1` |

### OpenAI (needs Codex)

| Model name | What runs |
|---|---|
| `codex` | Your Codex default model |
| `codex/<model>` | Any model your Codex accepts, e.g. `codex/gpt-5.5`. Run `codex` and type `/model` to see the list for your plan |

### Agent mode

Add `-agent` to any name above, e.g. `claude-code-agent/sonnet` or `codex-agent`. You can also use
`clibridge-agent` for the agent version of your `CLIBRIDGE_MODEL`. See [Agent mode](#agent-mode-optional).

Which models you can use depends on your Claude or ChatGPT plan.

**Your other models are not affected.** Only `clibridge` and the names above are handled by clibridge. `gpt-4o`,
`claude-sonnet-4-5` and every other name still go to the real API, with your real API key, as before.

---

## Thinking

### Set how hard the model thinks

Pick a level: `none`, `minimal`, `low`, `medium`, `high`, `xhigh` or `max`.

| Where | How |
|---|---|
| For everything | `CLIBRIDGE_EFFORT=high` in `.env` |
| OpenAI SDK | `reasoning_effort="high"` |
| OpenAI Responses | `reasoning={"effort": "high"}` |
| OpenAI Agents SDK | `model_settings=ModelSettings(reasoning=Reasoning(effort="high"))` |
| Anthropic SDK | `thinking={"type": "enabled", "budget_tokens": 10000}` (the budget picks a level), or `thinking={"type": "disabled"}` |
| LiteLLM | `extra_body={"reasoning_effort": "high"}`, or the `.env` setting |

How each level reaches the CLI:

| Level | Claude Code | Codex |
|---|---|---|
| `none` | thinking turned off | `none` |
| `minimal` | `low` | `low` |
| `low` / `medium` / `high` / `xhigh` | same | same |
| `max` | `max` | `xhigh` (its highest) |

### See what the model thought

| Where | Where the thinking shows up |
|---|---|
| OpenAI SDK | `reply.choices[0].message.reasoning_content` (streaming: `delta.reasoning_content`) |
| Anthropic SDK | `thinking` blocks before the text, when you turn thinking on |
| OpenAI Responses / Agents SDK | a `reasoning` item, when you set a reasoning effort |
| LiteLLM | `reply.choices[0].message.reasoning_content` (not while streaming) |
| Terminal | `clibridge ask -t "your question"` |

Two things to know:
- You get a **short summary** of the thinking, which is what the CLIs show, not the full raw thoughts.
- **The model decides when to think.** Easy questions often come back with no thinking at all.

---

## Agent mode (optional)

Normally the CLI acts as a **plain AI model**: no tools, run from an empty folder.

In agent mode (any model name ending in `-agent`), it works like a coding agent **inside a folder**, using its own
tools to read files, search and run commands. It's read-only unless you allow more:

```bash
CLIBRIDGE_WORKDIR=/path/to/my-project          # folder to work in (default: current folder)
CLIBRIDGE_PERMISSION_MODE=acceptEdits          # let Claude edit files
CLIBRIDGE_SANDBOX=workspace-write              # let Codex edit files
```

---

## All settings

Put these in `.env` or set them as environment variables. Environment variables win over `.env`.

| Setting | What it does | Default |
|---|---|---|
| `CLIBRIDGE_MODEL` | What `model="clibridge"` means | `claude-code` |
| `CLIBRIDGE_EFFORT` | Default thinking level | the CLI's default |
| `CLIBRIDGE_WORKDIR` | Folder for agent mode | current folder |
| `CLIBRIDGE_PERMISSION_MODE` | What Claude may do in agent mode, e.g. `acceptEdits` | read-only |
| `CLIBRIDGE_SANDBOX` | What Codex may do in agent mode: `read-only`, `workspace-write` | `read-only` |
| `CLIBRIDGE_MAX_CONCURRENCY` | CLI calls allowed at once | `4` |
| `CLIBRIDGE_TIMEOUT` | Seconds before a call is stopped | `600` |
| `CLIBRIDGE_CLAUDE_BIN` / `CLIBRIDGE_CODEX_BIN` | Path to the CLIs, if they aren't on your PATH | `claude` / `codex` |
| `CLIBRIDGE_ALIASES` | Extra model names, e.g. `fast=claude-code/haiku,smart=claude-code/opus` | none |
| `CLIBRIDGE_AUTOLOAD` | `0` turns off the automatic mode | on |
| `CLIBRIDGE_ENV_FILE` | Use this file instead of searching for `.env` | none |

clibridge looks for `.env` in the current folder, then in parent folders. It only reads the `CLIBRIDGE_` lines and
ignores everything else in the file.

---

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
clibridge ask "What is a monad?"              # quick test (uses CLIBRIDGE_MODEL)
clibridge ask -m codex "Write a regex for emails"
clibridge ask -e high -t "Is 391 prime?"      # think hard and show the thinking
clibridge doctor --ping                       # are the CLIs installed and logged in?
clibridge serve --help                        # all server options
```

## What works

- ✅ Chat and streaming
- ✅ Tool / function calling (so agents work)
- ✅ Structured output: JSON mode, JSON schema, Pydantic
- ✅ Thinking (level in, summary out)
- ✅ Images
- ✅ Sync and async

Ignored: `temperature`, `max_tokens`, `top_p`, `n`, `seed`, `logprobs`. The CLIs don't expose them.
Not available: embeddings, audio, image generation.

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
- **Prefer no automatic mode?** Set `CLIBRIDGE_AUTOLOAD=0` and opt in explicitly with `from clibridge import OpenAI`
  (also `AsyncOpenAI`, `Anthropic`) or `from clibridge.langchain import ChatClaudeCode`.

## Troubleshooting

| You see | Fix |
|---|---|
| `Missing credentials` / `api_key must be set` | clibridge isn't installed in this Python. Run `clibridge doctor` with the same Python |
| The wrong model answers | Run `clibridge doctor` from your project folder: it prints what `clibridge` means there |
| `Could not find the claude CLI` | Install it, or set `CLIBRIDGE_CLAUDE_BIN=/path/to/claude` |
| `Invalid API key · Please run /login` | Run `claude` and log in |
| `codex: ... usage limit` | You hit your plan's limit; wait for it to reset |
| No thinking comes back | The model skipped thinking for an easy question; try a harder one or `CLIBRIDGE_EFFORT=high` |
| LangChain `ChatOpenAI(model="codex")` returns a list | That's LangChain's Responses API format: use `.text`, or pass `use_responses_api=False` |

## Running the tests

The tests use small fake `claude` / `codex` scripts, so they don't need a login and don't use your quota.

```bash
pip install -e ".[dev]"
pytest
```
