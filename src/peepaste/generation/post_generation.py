from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class GenerationResult:
    package_dir: Path
    files: dict[str, Path]


class ProjectPackageManager:
    def __init__(self, package_dir: Path | str):
        self.package_dir = Path(package_dir)
        self.state_path = self.package_dir / "project_state.json"

    def load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            raise FileNotFoundError(f"Project state not found: {self.state_path}")
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def accept_title(self, title: str, accepted_by: str = "user") -> dict[str, Any]:
        state = self.load_state()
        state["title_state"] = "accepted"
        state["accepted_title"] = title
        state["accepted_by"] = accepted_by
        state["accepted_at"] = datetime.now(timezone.utc).isoformat()
        state.setdefault("gates", {})["silent_generation_ready"] = True
        self._write_json(self.state_path, state)
        return state

    def generate_after_acceptance(self) -> GenerationResult:
        state = self.load_state()
        if state.get("title_state") != "accepted" or not state.get("accepted_title"):
            raise ValueError("Post generation requires an accepted title.")
        latest_layout = self._latest_layout()
        files = {
            "project": self.package_dir / "project.json",
            "relations": self.package_dir / "relations.json",
            "summary": self.package_dir / "summary.md",
            "naming_plan": self.package_dir / "naming_plan.json",
            "manifest": self.package_dir / "materials_manifest.csv",
            "agent_context": self.package_dir / "agent_context.md",
            "openclaw_prompt": self.package_dir / "openclaw_prompt.md",
            "review_sheet": self.package_dir / "review_sheet.md",
            "clipboard_bundle": self.package_dir / "clipboard_bundle.txt",
        }
        self._write_json(files["project"], self._project_doc(state, latest_layout))
        self._write_json(files["relations"], self._relations_doc(latest_layout))
        files["summary"].write_text(self._summary_doc(state, latest_layout), encoding="utf-8")
        self._write_json(files["naming_plan"], self._naming_plan(state, latest_layout))
        self._write_manifest(files["manifest"], latest_layout)
        files["agent_context"].write_text(self._agent_context_doc(state, latest_layout), encoding="utf-8")
        files["openclaw_prompt"].write_text(self._openclaw_prompt_doc(state, latest_layout), encoding="utf-8")
        files["review_sheet"].write_text(self._review_sheet_doc(state, latest_layout), encoding="utf-8")
        files["clipboard_bundle"].write_text(self._clipboard_bundle_doc(state, latest_layout), encoding="utf-8")
        state["last_generated_at"] = datetime.now(timezone.utc).isoformat()
        state["generated_files"] = {name: str(path) for name, path in files.items()}
        self._write_json(self.state_path, state)
        return GenerationResult(self.package_dir, files)

    def _latest_layout(self) -> dict[str, Any]:
        record_dir = self.package_dir / "scene_records"
        layouts = sorted(record_dir.glob("*.layout.json"))
        if not layouts:
            raise FileNotFoundError(f"No layout records found in {record_dir}")
        return json.loads(layouts[-1].read_text(encoding="utf-8"))

    def _project_doc(self, state: dict[str, Any], layout: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema_version": "0.2",
            "title": state["accepted_title"],
            "title_state": state["title_state"],
            "source": layout["snapshot"]["source"],
            "latest_snapshot_at": layout["snapshot"]["captured_at"],
            "item_count": layout["compression"]["item_count"],
            "group_count": layout["compression"]["group_count"],
            "semantic_risk": layout["gates"]["semantic_risk"],
            "post_generation_policy": "generated_after_title_acceptance",
        }

    def _relations_doc(self, layout: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema_version": "0.2",
            "mode": "mode_1_structure",
            "facts": layout["facts"],
            "relations": layout["relations"],
            "groups": layout["groups"],
            "structures": layout["structures"],
            "gates": layout["gates"],
            "note": "These are structural candidates, not confirmed semantic truths.",
        }

    def _summary_doc(self, state: dict[str, Any], layout: dict[str, Any]) -> str:
        return (
            f"# {state['accepted_title']}\n\n"
            "## English\n\n"
            f"{layout['layout_message']['en']}\n\n"
            "## 中文\n\n"
            f"{layout['layout_message']['zh']}\n\n"
            "## Generation State\n\n"
            "- Title accepted before project-level generation.\n"
            f"- Semantic risk: `{layout['gates']['semantic_risk']}`.\n"
            f"- Image reading needed: `{layout['gates']['needs_image_reading']}`.\n"
        )

    def _naming_plan(self, state: dict[str, Any], layout: dict[str, Any]) -> dict[str, Any]:
        risk = layout["gates"]["semantic_risk"]
        profile = "neutral_timestamp" if risk != "low" else "structure_based"
        return {
            "schema_version": "0.2",
            "title": state["accepted_title"],
            "profile": profile,
            "rules": [
                "Keep original source reference when available.",
                "Use neutral timestamp names for mixed or uncertain scenes.",
                "Use group prefixes only after stable grouping is detected.",
            ],
        }

    def _write_manifest(self, path: Path, layout: dict[str, Any]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["id", "title", "source_ref", "x", "y", "width", "height"])
            writer.writeheader()
            for item in layout["snapshot"]["items"]:
                writer.writerow(
                    {
                        "id": item["id"],
                        "title": item.get("title", ""),
                        "source_ref": item.get("source_ref", ""),
                        "x": item["x"],
                        "y": item["y"],
                        "width": item["width"],
                        "height": item["height"],
                    }
                )

    def _agent_context_doc(self, state: dict[str, Any], layout: dict[str, Any]) -> str:
        structures = ", ".join(sorted({item["type"] for item in layout["structures"]})) or "none"
        return (
            f"# Agent Context: {state['accepted_title']}\n\n"
            "This package contains a ScenePack visual scene record.\n\n"
            f"- Items: {layout['compression']['item_count']}\n"
            f"- Groups: {layout['compression']['group_count']}\n"
            f"- Structures: {structures}\n"
            f"- Semantic risk: {layout['gates']['semantic_risk']}\n"
            f"- Needs image reading: {layout['gates']['needs_image_reading']}\n\n"
            "Use layout relations as structural hints, not as confirmed semantic facts.\n"
        )

    def _openclaw_prompt_doc(self, state: dict[str, Any], layout: dict[str, Any]) -> str:
        return (
            f"# OpenClaw Handoff: {state['accepted_title']}\n\n"
            "You are receiving a ScenePack visual scene package. Use the user's accepted title as the anchor, "
            "then inspect the structural evidence before making semantic claims.\n\n"
            "## User-Confirmed Title\n\n"
            f"{state['accepted_title']}\n\n"
            "## Scene Summary\n\n"
            f"- English: {layout['layout_message']['en']}\n"
            f"- 中文: {layout['layout_message']['zh']}\n"
            f"- Semantic risk: `{layout['gates']['semantic_risk']}`\n"
            f"- Needs image reading: `{layout['gates']['needs_image_reading']}`\n\n"
            "## Key References To Check\n\n"
            f"{_material_reference_lines(layout)}\n\n"
            "## Working Rules\n\n"
            "- Do not infer private or semantic content from geometry alone.\n"
            "- Ask for image reading or user confirmation when the semantic risk is medium or high.\n"
            "- Preserve source references and item IDs in any follow-up plan.\n"
        )

    def _review_sheet_doc(self, state: dict[str, Any], layout: dict[str, Any]) -> str:
        return (
            f"# Review Sheet: {state['accepted_title']}\n\n"
            "## Confirm Before Generation\n\n"
            "- [ ] The accepted title matches the real user intent.\n"
            "- [ ] The key references below are relevant.\n"
            "- [ ] Image reading permission is clear when needed.\n"
            "- [ ] The package is safe to hand to OpenClaw.\n\n"
            "## 需要确认\n\n"
            "- [ ] 标题是否符合用户真实意图。\n"
            "- [ ] 下方关键参考是否真的相关。\n"
            "- [ ] 如需读图，权限是否明确。\n"
            "- [ ] 是否可以交给 OpenClaw 继续处理。\n\n"
            "## Key References\n\n"
            f"{_material_reference_lines(layout)}\n"
        )

    def _clipboard_bundle_doc(self, state: dict[str, Any], layout: dict[str, Any]) -> str:
        structures = ", ".join(sorted({item["type"] for item in layout["structures"]})) or "none"
        return (
            f"ScenePack package: {state['accepted_title']}\n"
            f"English summary: {layout['layout_message']['en']}\n"
            f"中文摘要: {layout['layout_message']['zh']}\n"
            f"Items: {layout['compression']['item_count']}; Groups: {layout['compression']['group_count']}; Structures: {structures}\n"
            f"Semantic risk: {layout['gates']['semantic_risk']}; Needs image reading: {layout['gates']['needs_image_reading']}\n"
            "Key references:\n"
            f"{_material_reference_lines(layout)}\n"
            "Rule: use these as structural hints; confirm meaning before generation.\n"
        )

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _material_reference_lines(layout: dict[str, Any], limit: int = 12) -> str:
    lines = []
    for item in layout["snapshot"]["items"][:limit]:
        label = item.get("title") or item.get("process") or item["id"]
        source = item.get("source_ref") or "no source reference"
        box = f"{int(item['x'])},{int(item['y'])},{int(item['width'])}x{int(item['height'])}"
        lines.append(f"- `{item['id']}` {label} | source: `{source}` | box: `{box}`")
    return "\n".join(lines) or "- None"
