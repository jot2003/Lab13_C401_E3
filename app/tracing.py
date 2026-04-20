from __future__ import annotations

import os
from typing import Any, Mapping

try:
    from langfuse.decorators import observe, langfuse_context
except Exception:  # pragma: no cover
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
        langfuse_context.update_current_trace(**kwargs)
    except Exception:  # pragma: no cover
        return None


def safe_update_current_observation(**kwargs: Any) -> None:
    try:
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
