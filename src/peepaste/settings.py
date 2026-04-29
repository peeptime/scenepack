from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AppearanceSettings:
    theme: str = "light"
    language: str = "en"
    accent_color: str = "#2563eb"
    font_family: str = "Segoe UI"
    font_size: int = 12


@dataclass
class PrivacySettings:
    read_images_by_default: bool = False
    upload_images_by_default: bool = False
    log_private_text: bool = False


@dataclass
class AiSettings:
    enabled: bool = False
    provider: str = "openai"
    api_key_env: str = "OPENAI_API_KEY"
    model: str = ""
    token_budget: int = 4000


@dataclass
class SkillSettings:
    title_patterns: list[str] = field(
        default_factory=lambda: [
            "{kind}_{date}",
            "{kind}_{zone_count}zones_{date}",
            "visual_scene_{date}",
        ]
    )
    naming_profiles: dict[str, str] = field(
        default_factory=lambda: {
            "mixed": "neutral_timestamp",
            "project_management": "task_evidence",
            "image_material": "visual_material",
            "ai_coding": "prompt_context_result",
            "product_research": "competitor_feature_evidence",
        }
    )
    ignored_structure_signals: list[str] = field(default_factory=list)
    trusted_downstream_targets: list[str] = field(default_factory=lambda: ["agent_context", "markdown"])


@dataclass
class InstallSettings:
    initialized: bool = False
    install_channel: str = "internal"
    startup_on_login: bool = False
    open_gui_on_start: bool = True
    auto_monitor: bool = False
    monitor_interval_seconds: float = 1.5
    stable_capture_ticks: int = 2
    platform_target: str = "windows_11"
    snipaste_min_version: str = "2.10.8"
    snipaste_max_version: str = "2.11.3"


@dataclass
class AppSettings:
    schema_version: str = "0.2"
    storage_root: str = ".peepaste-runs/projects"
    capture_filter: str = "Snipaste"
    appearance: AppearanceSettings = field(default_factory=AppearanceSettings)
    privacy: PrivacySettings = field(default_factory=PrivacySettings)
    ai: AiSettings = field(default_factory=AiSettings)
    skills: SkillSettings = field(default_factory=SkillSettings)
    install: InstallSettings = field(default_factory=InstallSettings)

    @classmethod
    def default_path(cls) -> Path:
        base = os.environ.get("PEEPASTE_CONFIG_DIR")
        if base:
            return Path(base) / "settings.json"
        return Path.home() / "AppData" / "Roaming" / "ScenePack" / "settings.json"

    @classmethod
    def load(cls, path: Path | str | None = None) -> "AppSettings":
        target = Path(path) if path else cls.default_path()
        if not target.exists():
            return cls()
        data = json.loads(target.read_text(encoding="utf-8"))
        return cls.from_mapping(data)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "AppSettings":
        return cls(
            schema_version=str(data.get("schema_version", "0.2")),
            storage_root=os.path.expandvars(str(data.get("storage_root", ".peepaste-runs/projects"))),
            capture_filter=str(data.get("capture_filter", "Snipaste")),
            appearance=AppearanceSettings(**dict(data.get("appearance", {}))),
            privacy=PrivacySettings(**dict(data.get("privacy", {}))),
            ai=AiSettings(**dict(data.get("ai", {}))),
            skills=SkillSettings(**dict(data.get("skills", {}))),
            install=InstallSettings(**dict(data.get("install", {}))),
        )

    def save(self, path: Path | str | None = None) -> Path:
        target = Path(path) if path else self.default_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8")
        return target

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
