from __future__ import annotations

import os
from typing import Any, Mapping

_LANGFUSE_MODE = "none"

try:
    from langfuse.decorators import observe, langfuse_context
    _LANGFUSE_MODE = "decorators-v2"
except Exception:  # pragma: no cover
    try:
        from langfuse import get_client, observe

        langfuse_context = get_client()
        _LANGFUSE_MODE = "client-v3"
    except Exception:
        def observe(*args: Any, **kwargs: Any):
            def decorator(func):
                return func
            return decorator

        class _DummyContext:
            def update_current_trace(self, **kwargs: Any) -> None:
                return None

            def update_current_observation(self, **kwargs: Any) -> None:
                return None

        langfuse_context = _DummyContext()


def safe_update_current_trace(**kwargs: Any) -> None:
    try:
        if hasattr(langfuse_context, "update_current_trace"):
            langfuse_context.update_current_trace(**kwargs)
    except Exception:  # pragma: no cover
        return None


def safe_update_current_observation(**kwargs: Any) -> None:
    try:
        if _LANGFUSE_MODE == "client-v3" and hasattr(langfuse_context, "update_current_span"):
            metadata = kwargs.get("metadata") or {}
            if not isinstance(metadata, dict):
                metadata = {"value": metadata}

            # Keep v2-style fields while mapping to v3-compatible span updates.
            if kwargs.get("model") is not None:
                metadata["model"] = kwargs["model"]
            if kwargs.get("usage_details") is not None:
                metadata["usage_details"] = kwargs["usage_details"]

            span_kwargs = {
                "name": kwargs.get("name"),
                "input": kwargs.get("input"),
                "output": kwargs.get("output"),
                "metadata": metadata or None,
                "version": kwargs.get("version"),
                "level": kwargs.get("level"),
                "status_message": kwargs.get("status_message"),
            }
            filtered_span_kwargs = {key: value for key, value in span_kwargs.items() if value is not None}
            langfuse_context.update_current_span(**filtered_span_kwargs)
            return None

        if hasattr(langfuse_context, "update_current_observation"):
            langfuse_context.update_current_observation(**kwargs)
    except Exception:  # pragma: no cover
        return None


def extract_active_incidents(incidents: Mapping[str, bool]) -> list[str]:
    return sorted([name for name, enabled in incidents.items() if enabled])


def build_trace_tags(feature: str, model: str, active_incidents: list[str], env: str) -> list[str]:
    tags = ["lab", feature, model, f"feature:{feature}", f"model:{model}", f"env:{env}"]
    tags.extend(f"incident:{name}" for name in active_incidents)
    return tags


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
