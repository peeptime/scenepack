from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from peepaste.settings import AppSettings


@dataclass
class AiRequest:
    purpose: str
    layout_summary: dict[str, Any]
    user_text: str = ""
    image_refs: list[str] = field(default_factory=list)


@dataclass
class AiResponse:
    provider: str
    title_candidates: list[dict[str, Any]]
    summary: str
    token_estimate: int = 0
    used_image_reading: bool = False


class AiAdapter(Protocol):
    def complete(self, request: AiRequest) -> AiResponse:
        ...


class NullAiAdapter:
    provider = "none"

    def complete(self, request: AiRequest) -> AiResponse:
        return AiResponse(
            provider=self.provider,
            title_candidates=[],
            summary="AI mode is not enabled. Structural mode remains active.",
            token_estimate=0,
            used_image_reading=False,
        )


def create_ai_adapter(settings: AppSettings) -> AiAdapter:
    if not settings.ai.enabled:
        return NullAiAdapter()
    # Real providers are intentionally deferred. The adapter boundary is stable
    # enough for GUI/settings work without leaking secrets into logs or Git.
    return NullAiAdapter()

