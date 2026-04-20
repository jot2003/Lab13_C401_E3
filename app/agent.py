from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass

from . import metrics
from .incidents import status as incident_status
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import (
    build_trace_tags,
    extract_active_incidents,
    observe,
    safe_update_current_observation,
    safe_update_current_trace,
)


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    @observe(name="agent.run")
    def run(
        self,
        user_id: str,
        feature: str,
        session_id: str,
        message: str,
        correlation_id: str | None = None,
    ) -> AgentResult:
        started = time.perf_counter()
        resolved_correlation_id = self._resolve_correlation_id(correlation_id)
        active_incidents = extract_active_incidents(incident_status())
        docs = self._retrieve_docs(
            message=message,
            correlation_id=resolved_correlation_id,
            feature=feature,
            session_id=session_id,
            active_incidents=active_incidents,
        )
        prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"
        response = self._generate_response(
            prompt=prompt,
            correlation_id=resolved_correlation_id,
            feature=feature,
            session_id=session_id,
            active_incidents=active_incidents,
        )
        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        cost_usd = self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens)
        env = os.getenv("APP_ENV", "dev")

        safe_update_current_trace(
            name=f"chat:{feature}",
            user_id=hash_user_id(user_id),
            session_id=session_id,
            tags=build_trace_tags(feature=feature, model=self.model, active_incidents=active_incidents, env=env),
            metadata={
                "correlation_id": resolved_correlation_id,
                "active_incidents": active_incidents,
                "feature": feature,
                "model": self.model,
            },
        )
        safe_update_current_observation(
            model=self.model,
            input={"message_preview": summarize_text(message)},
            output={"answer_preview": summarize_text(response.text), "quality_score": quality_score},
            metadata={
                "doc_count": len(docs),
                "query_preview": summarize_text(message),
                "latency_ms": latency_ms,
                "cost_usd": cost_usd,
                "correlation_id": resolved_correlation_id,
                "session_id": session_id,
                "feature": feature,
                "model": self.model,
                "active_incidents": active_incidents,
            },
            usage_details={"input": response.usage.input_tokens, "output": response.usage.output_tokens},
        )

        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
        )

        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
        )

    @observe(name="rag.retrieve")
    def _retrieve_docs(
        self,
        message: str,
        correlation_id: str,
        feature: str,
        session_id: str,
        active_incidents: list[str],
    ) -> list[str]:
        docs = retrieve(message)
        safe_update_current_observation(
            input={"message_preview": summarize_text(message)},
            output={"doc_count": len(docs)},
            metadata={
                "doc_count": len(docs),
                "query_preview": summarize_text(message),
                "correlation_id": correlation_id,
                "feature": feature,
                "session_id": session_id,
                "active_incidents": active_incidents,
            },
        )
        return docs

    @observe(name="llm.generate")
    def _generate_response(
        self,
        prompt: str,
        correlation_id: str,
        feature: str,
        session_id: str,
        active_incidents: list[str],
    ):
        response = self.llm.generate(prompt)
        safe_update_current_observation(
            model=self.model,
            metadata={
                "prompt_preview": summarize_text(prompt, max_len=120),
                "correlation_id": correlation_id,
                "feature": feature,
                "session_id": session_id,
                "model": self.model,
                "active_incidents": active_incidents,
            },
            usage_details={"input": response.usage.input_tokens, "output": response.usage.output_tokens},
        )
        return response

    def _resolve_correlation_id(self, correlation_id: str | None) -> str:
        if correlation_id and correlation_id.strip():
            return correlation_id.strip()
        return f"req-local-{uuid.uuid4().hex[:8]}"

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
