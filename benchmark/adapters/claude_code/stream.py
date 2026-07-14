"""Public Claude Code stream-json parsing helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


ARF_PLUGIN = "arf-academic"


@dataclass(frozen=True)
class ClaudeStreamObservation:
    """Public observations parsed from Claude Code stream-json output."""

    plugin_loaded: bool | None = None
    plugin_load_error: str | None = None
    observed_skills: tuple[str, ...] = ()
    response_text: str | None = None
    raw_response_available: bool = False
    parse_error: str | None = None


def parse_claude_stream(stdout: str) -> ClaudeStreamObservation:
    """Parse newline-delimited JSON emitted by Claude Code stream-json mode."""

    plugin_loaded: bool | None = None
    plugin_load_error: str | None = None
    observed_skills: list[str] = []
    assistant_texts: list[str] = []
    final_result: str | None = None

    for line_number, line in enumerate(stdout.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return ClaudeStreamObservation(
                parse_error=f"malformed JSON in Claude stream at line {line_number}"
            )
        if not isinstance(event, dict):
            continue

        loaded, load_error = _plugin_observation(event)
        if loaded is not None:
            plugin_loaded = loaded
        if load_error is not None:
            plugin_loaded = False
            plugin_load_error = load_error

        observed_skills.extend(_skill_invocations(event))

        result_text = _result_text(event)
        if result_text is not None:
            final_result = result_text
        assistant_texts.extend(_assistant_texts(event))

    response_text = final_result
    if response_text is None and assistant_texts:
        response_text = "\n".join(assistant_texts)

    return ClaudeStreamObservation(
        plugin_loaded=plugin_loaded,
        plugin_load_error=plugin_load_error,
        observed_skills=tuple(observed_skills),
        response_text=response_text,
        raw_response_available=response_text is not None,
    )


def _plugin_observation(event: dict[str, Any]) -> tuple[bool | None, str | None]:
    if not _is_system_init(event):
        return None, None

    for key in ("plugin_errors", "failed_plugins", "errors"):
        error = _find_plugin_error(event.get(key))
        if error is not None:
            return False, error

    for key in ("plugins", "loaded_plugins", "enabled_plugins"):
        if _contains_loaded_plugin(event.get(key)):
            return True, None

    plugin_info = event.get("plugin_info")
    if isinstance(plugin_info, dict):
        error = _find_plugin_error(plugin_info.get("errors"))
        if error is not None:
            return False, error
        for key in ("plugins", "loaded", "enabled"):
            if _contains_loaded_plugin(plugin_info.get(key)):
                return True, None

    return None, None


def _is_system_init(event: dict[str, Any]) -> bool:
    event_type = event.get("type")
    subtype = event.get("subtype") or event.get("event")
    return event_type == "system/init" or (
        event_type == "system" and subtype == "init"
    )


def _contains_loaded_plugin(value: Any) -> bool:
    if isinstance(value, str):
        return value == ARF_PLUGIN
    if isinstance(value, dict):
        name = value.get("name") or value.get("id")
        status = value.get("status") or value.get("state")
        if name == ARF_PLUGIN:
            return status in (None, "loaded", "enabled", "ok", "success")
        return any(_contains_loaded_plugin(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_loaded_plugin(item) for item in value)
    return False


def _find_plugin_error(value: Any) -> str | None:
    if isinstance(value, str):
        return value if ARF_PLUGIN in value else None
    if isinstance(value, dict):
        name = value.get("name") or value.get("id") or value.get("plugin")
        if name == ARF_PLUGIN:
            message = value.get("error") or value.get("message") or "plugin load error"
            return _sanitize_error(str(message))
        return next(
            (error for error in (_find_plugin_error(item) for item in value.values()) if error),
            None,
        )
    if isinstance(value, list):
        return next(
            (error for error in (_find_plugin_error(item) for item in value) if error),
            None,
        )
    return None


def _sanitize_error(error: str) -> str:
    return " ".join(error.split())


def _skill_invocations(value: Any) -> tuple[str, ...]:
    skills: list[str] = []
    if isinstance(value, dict):
        if _is_skill_tool_use(value):
            skill = _skill_from_tool_input(value.get("input"))
            if skill is not None:
                skills.append(skill)
        for item in value.values():
            skills.extend(_skill_invocations(item))
    elif isinstance(value, list):
        for item in value:
            skills.extend(_skill_invocations(item))
    return tuple(skills)


def _is_skill_tool_use(value: dict[str, Any]) -> bool:
    return value.get("type") == "tool_use" and value.get("name") == "Skill"


def _skill_from_tool_input(value: Any) -> str | None:
    candidate: str | None = None
    if isinstance(value, str):
        candidate = value
    elif isinstance(value, dict):
        for key in ("skill", "skill_id", "skill_name", "command"):
            if isinstance(value.get(key), str):
                candidate = value[key]
                break
    if candidate is None:
        return None
    normalized = candidate.strip()
    if normalized.startswith("/"):
        normalized = normalized[1:]
    if normalized.startswith(f"{ARF_PLUGIN}:"):
        return normalized
    return None


def _result_text(event: dict[str, Any]) -> str | None:
    if event.get("type") == "result" and isinstance(event.get("result"), str):
        return event["result"]
    return None


def _assistant_texts(event: dict[str, Any]) -> tuple[str, ...]:
    message = event.get("message")
    if isinstance(message, dict) and message.get("role") == "assistant":
        return _text_blocks(message.get("content"))
    if event.get("type") == "assistant":
        return _text_blocks(event.get("content"))
    return ()


def _text_blocks(content: Any) -> tuple[str, ...]:
    if isinstance(content, str):
        return (content,)
    if not isinstance(content, list):
        return ()
    texts: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str):
                texts.append(text)
    return tuple(texts)
