"""LiteLLM custom providers backed by the local CLIs.

    import litellm
    import clibridge.litellm

    clibridge.litellm.register()
    litellm.completion(model="claude-code/sonnet", messages=[{"role": "user", "content": "hi"}])

Providers: ``claude-code``, ``claude-code-agent``, ``codex``, ``codex-agent``.
The part after the slash is the CLI model (``default`` for the CLI's default).
"""

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional

import litellm
from litellm.llms.custom_llm import CustomLLM, CustomLLMError
from litellm.types.utils import ModelResponse

from . import openai_api
from .config import BridgeConfig
from .core import ChatItem, aiter_chat, acomplete_chat, complete_chat, iter_chat
from .errors import BridgeError

PROVIDERS = ("claude-code", "claude-code-agent", "codex", "codex-agent")
_PARAMS = ("tools", "tool_choice", "parallel_tool_calls", "response_format", "stop", "reasoning_effort",
           "functions", "function_call")
_EXTRA = ("agent", "cwd", "max_turns")


def _chunk(text: str = "", tool_use: Any = None, finish: str = "", usage: Any = None) -> Dict[str, Any]:
    return {"text": text, "tool_use": tool_use, "is_finished": bool(finish), "finish_reason": finish,
            "usage": usage, "index": 0}


def _stream_chunks(item: ChatItem) -> List[Dict[str, Any]]:
    if isinstance(item, str):
        return [_chunk(item)]
    chunks = []
    if item.content and not item.streamed:
        chunks.append(_chunk(item.content))
    for i, call in enumerate(item.tool_calls):
        chunks.append(_chunk(tool_use={"id": call.id, "type": "function", "index": i,
                                       "function": {"name": call.name, "arguments": call.arguments}}))
    usage = {"prompt_tokens": item.prompt_tokens, "completion_tokens": item.completion_tokens,
             "total_tokens": item.prompt_tokens + item.completion_tokens}
    chunks.append(_chunk(finish=item.finish_reason, usage=usage))
    return chunks


def _error(exc: BridgeError) -> CustomLLMError:
    return CustomLLMError(status_code=exc.status, message=str(exc))


class CLIBridgeLLM(CustomLLM):
    def __init__(self, provider: str, config: Optional[BridgeConfig] = None):
        super().__init__()
        self.provider = provider
        self.config = config or BridgeConfig()

    def _request(self, model: str, messages: list, kwargs: Dict[str, Any], stream: bool) -> Dict[str, Any]:
        params = kwargs.get("optional_params") or {}
        request: Dict[str, Any] = {
            "model": f"{self.provider}/{model}" if model else self.provider,
            "messages": messages,
            "stream": stream,
        }
        request.update({k: params[k] for k in _PARAMS if k in params})
        extra = params.get("extra_body") or {}
        request.update({k: extra[k] for k in _EXTRA if k in extra})
        return request

    def completion(self, model: str, messages: list, *args: Any, **kwargs: Any) -> ModelResponse:
        request = self._request(model, messages, kwargs, stream=False)
        try:
            result = complete_chat(request, self.config)
        except BridgeError as exc:
            raise _error(exc) from exc
        return ModelResponse(**openai_api.completion(result, request))

    async def acompletion(self, model: str, messages: list, *args: Any, **kwargs: Any) -> ModelResponse:
        request = self._request(model, messages, kwargs, stream=False)
        try:
            result = await acomplete_chat(request, self.config)
        except BridgeError as exc:
            raise _error(exc) from exc
        return ModelResponse(**openai_api.completion(result, request))

    def streaming(self, model: str, messages: list, *args: Any, **kwargs: Any) -> Iterator[Dict[str, Any]]:
        request = self._request(model, messages, kwargs, stream=True)
        try:
            for item in iter_chat(request, self.config):
                yield from _stream_chunks(item)
        except BridgeError as exc:
            raise _error(exc) from exc

    async def astreaming(self, model: str, messages: list, *args: Any, **kwargs: Any):
        request = self._request(model, messages, kwargs, stream=True)
        try:
            async for item in aiter_chat(request, self.config):
                for chunk in _stream_chunks(item):
                    yield chunk
        except BridgeError as exc:
            raise _error(exc) from exc


def register(config: Optional[BridgeConfig] = None) -> None:
    """Add the clibridge providers to ``litellm.custom_provider_map``."""
    existing = [p for p in litellm.custom_provider_map if p.get("provider") not in PROVIDERS]
    litellm.custom_provider_map = existing + [
        {"provider": name, "custom_handler": CLIBridgeLLM(name, config)} for name in PROVIDERS
    ]
