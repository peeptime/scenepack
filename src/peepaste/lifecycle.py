from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ScenePhase(str, Enum):
    SILENT_CAPTURE = "silent_capture"
    NEEDS_CONFIRMATION = "needs_confirmation"
    READY_TO_HANDOFF = "ready_to_handoff"
    HANDED_OFF = "handed_off"


@dataclass
class SceneLifecycle:
    phase: ScenePhase = ScenePhase.SILENT_CAPTURE
    package_dir: Path | None = None
    accepted_title: str = ""
    last_event: str = "idle"
    handoff_files: dict[str, Path] = field(default_factory=dict)

    @property
    def can_generate(self) -> bool:
        return self.phase == ScenePhase.NEEDS_CONFIRMATION and bool(self.package_dir and self.accepted_title)

    @property
    def can_handoff(self) -> bool:
        return self.phase in {ScenePhase.READY_TO_HANDOFF, ScenePhase.HANDED_OFF} and bool(self.handoff_files)

    def captured(self, package_dir: Path) -> None:
        self.phase = ScenePhase.NEEDS_CONFIRMATION
        self.package_dir = package_dir
        self.accepted_title = ""
        self.handoff_files = {}
        self.last_event = "stable_scene_recorded"

    def title_selected(self, title: str) -> None:
        self.accepted_title = title.strip()
        self.last_event = "title_selected" if self.accepted_title else "title_cleared"

    def generated(self, files: dict[str, Path]) -> None:
        self.phase = ScenePhase.READY_TO_HANDOFF
        self.handoff_files = dict(files)
        self.last_event = "handoff_ready"

    def handed_off(self) -> None:
        if self.can_handoff:
            self.phase = ScenePhase.HANDED_OFF
            self.last_event = "handoff_copied_or_dragged"


def phase_label(phase: ScenePhase, language: str = "en") -> str:
    labels = {
        "en": {
            ScenePhase.SILENT_CAPTURE: "Silent capture",
            ScenePhase.NEEDS_CONFIRMATION: "Needs confirmation",
            ScenePhase.READY_TO_HANDOFF: "Ready to handoff",
            ScenePhase.HANDED_OFF: "Handed off",
        },
        "zh": {
            ScenePhase.SILENT_CAPTURE: "旁路记录",
            ScenePhase.NEEDS_CONFIRMATION: "等待确认",
            ScenePhase.READY_TO_HANDOFF: "可交接",
            ScenePhase.HANDED_OFF: "已交接",
        },
    }
    return labels.get(language, labels["en"]).get(phase, phase.value)
