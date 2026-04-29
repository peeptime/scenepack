from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from peepaste.models import StructureAnalysis


class ProjectPackageWriter:
    def __init__(self, root: Path | str):
        self.root = Path(root)

    def write_record(self, analysis: StructureAnalysis) -> dict[str, Path]:
        self.root.mkdir(parents=True, exist_ok=True)
        scene_records = self.root / "scene_records"
        scene_records.mkdir(exist_ok=True)
        timestamp = _safe_timestamp(analysis.snapshot.captured_at)
        layout_path = scene_records / f"{timestamp}.layout.json"
        message_path = scene_records / f"{timestamp}.message.md"
        state_path = self.root / "project_state.json"
        self._write_json(layout_path, analysis.to_dict())
        message_path.write_text(_message_markdown(analysis), encoding="utf-8")
        self._write_json(state_path, _project_state(analysis))
        return {"layout": layout_path, "message": message_path, "state": state_path}

    def _write_json(self, path: Path, data: dict) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _safe_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        parsed = datetime.now(timezone.utc)
    return parsed.strftime("%Y%m%dT%H%M%S")


def _message_markdown(analysis: StructureAnalysis) -> str:
    candidates = analysis.title_candidates
    title_lines = "\n".join([f"- {candidate['title']} ({candidate['confidence']})" for candidate in candidates]) or "- None"
    item_lines = "\n".join(
        [
            f"- `{item.id}` {item.title or item.process or 'Untitled'} "
            f"({int(item.x)}, {int(item.y)}, {int(item.width)}x{int(item.height)})"
            for item in analysis.snapshot.items[:12]
        ]
    ) or "- None"
    return (
        "# ScenePack Layout Message\n\n"
        "## Quick Confirmation\n\n"
        "- Confirm whether the title candidate matches the user's real intent.\n"
        "- Treat structure signals as layout evidence, not semantic truth.\n"
        "- Open key image or source references before downstream generation when risk is not low.\n\n"
        "## English\n\n"
        f"{analysis.layout_message['en']}\n\n"
        "## 中文\n\n"
        f"{analysis.layout_message['zh']}\n\n"
        "## Title Candidates\n\n"
        f"{title_lines}\n\n"
        "## Key References\n\n"
        f"{item_lines}\n"
    )


def _project_state(analysis: StructureAnalysis) -> dict:
    return {
        "schema_version": "0.1",
        "product": "ScenePack",
        "mode": "mode_1_structure",
        "title_state": "candidate",
        "accepted_title": None,
        "latest_snapshot_at": analysis.snapshot.captured_at,
        "latest_source": analysis.snapshot.source,
        "title_candidates": analysis.title_candidates,
        "gates": analysis.gates,
        "created_by": "peepaste-prototype",
    }
