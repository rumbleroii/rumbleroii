"""model="clibridge", .env files and aliases."""

import pytest

from clibridge import BridgeConfig, complete_chat, resolve_model
from clibridge.config import _parse_dotenv, dotenv_values, is_bridge_model


def test_clibridge_defaults_to_claude_code():
    assert resolve_model("clibridge") == resolve_model("claude-code")


def test_clibridge_follows_the_configured_model():
    route = resolve_model("clibridge", bridge_model="codex/gpt-5.5")
    assert (route.backend, route.model, route.agent) == ("codex", "gpt-5.5", False)
    assert resolve_model("clibridge-agent", bridge_model="claude-code/opus").agent
    assert resolve_model("clibridge", bridge_model="clibridge").backend == "claude"  # no loop


def test_is_bridge_model():
    for name in ("clibridge", "clibridge-agent", "claude-code/opus", "codex", "codex-agent/x"):
        assert is_bridge_model(name)
    for name in ("gpt-4o", "claude-sonnet-4-5", "codex-mini-latest", "", None):
        assert not is_bridge_model(name)


def test_parse_dotenv():
    text = """
# comment
CLIBRIDGE_MODEL=codex/gpt-5.5   # inline comment
export CLIBRIDGE_EFFORT="high"
CLIBRIDGE_ALIASES='fast=claude-code/haiku'
OPENAI_API_KEY=sk-should-be-ignored
not a setting
"""
    assert _parse_dotenv(text) == {
        "CLIBRIDGE_MODEL": "codex/gpt-5.5",
        "CLIBRIDGE_EFFORT": "high",
        "CLIBRIDGE_ALIASES": "fast=claude-code/haiku",
    }


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A project folder with a .env, used as the current directory (from a subfolder)."""
    (tmp_path / ".env").write_text("CLIBRIDGE_MODEL=codex/gpt-5.5\nCLIBRIDGE_EFFORT=high\n")
    sub = tmp_path / "src"
    sub.mkdir()
    monkeypatch.chdir(sub)
    monkeypatch.delenv("CLIBRIDGE_ENV_FILE")
    return tmp_path


def test_dotenv_is_found_in_parent_directories(project):
    assert dotenv_values()["CLIBRIDGE_MODEL"] == "codex/gpt-5.5"
    config = BridgeConfig()
    assert (config.model, config.effort) == ("codex/gpt-5.5", "high")


def test_environment_beats_dotenv(project, monkeypatch):
    monkeypatch.setenv("CLIBRIDGE_MODEL", "claude-code/opus")
    assert BridgeConfig().model == "claude-code/opus"


def test_dotenv_changes_are_picked_up(project):
    assert BridgeConfig().model == "codex/gpt-5.5"
    env = project / ".env"
    env.write_text("CLIBRIDGE_MODEL=claude-code/haiku\n")
    import os
    os.utime(env, (1, 1))  # make sure the mtime changes
    assert BridgeConfig().model == "claude-code/haiku"


def test_explicit_env_file(tmp_path, monkeypatch):
    path = tmp_path / "settings.env"
    path.write_text("CLIBRIDGE_MODEL=codex\n")
    monkeypatch.setenv("CLIBRIDGE_ENV_FILE", str(path))
    assert BridgeConfig().model == "codex"


def test_request_with_clibridge_model_uses_dotenv(project, calls):
    from .conftest import FAKE_CLI

    config = BridgeConfig(claude_bin=str(FAKE_CLI / "claude"), codex_bin=str(FAKE_CLI / "codex"))
    result = complete_chat({"model": "clibridge", "messages": [{"role": "user", "content": "hi"}]}, config)
    assert result.content == "pong from gpt-5.5: hi"
    argv = calls()[0]["argv"]
    assert argv[argv.index("--config") + 1] == 'model_reasoning_effort="high"'


def test_aliases(monkeypatch):
    monkeypatch.setenv("CLIBRIDGE_ALIASES", "inhouse=claude-code/sonnet, fast=codex")
    assert resolve_model("inhouse").model == "sonnet"
    assert resolve_model("fast").backend == "codex"
    assert is_bridge_model("inhouse")
