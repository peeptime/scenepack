from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RectItem:
    id: str
    x: float
    y: float
    width: float
    height: float
    title: str = ""
    source_ref: str = ""
    process: str = ""
    class_name: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.height)

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)

    @classmethod
    def from_mapping(cls, data: dict[str, Any], fallback_id: str) -> "RectItem":
        return cls(
            id=str(data.get("id") or fallback_id),
            x=float(data.get("x", 0)),
            y=float(data.get("y", 0)),
            width=float(data.get("width", 0)),
            height=float(data.get("height", 0)),
            title=str(data.get("title", "")),
            source_ref=str(data.get("source_ref") or data.get("path") or data.get("window_id") or ""),
            process=str(data.get("process", "")),
            class_name=str(data.get("class_name", "")),
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LayoutSnapshot:
    items: list[RectItem]
    captured_at: str = field(default_factory=lambda: datetime.now().astimezone().isoformat())
    source: str = "manual"
    snapshot_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "LayoutSnapshot":
        raw_items = data.get("items", data if isinstance(data, list) else [])
        if not isinstance(raw_items, list):
            raise ValueError("Layout snapshot must contain an items list.")
        items = [RectItem.from_mapping(item, f"item_{index + 1:03d}") for index, item in enumerate(raw_items)]
        return cls(
            items=items,
            captured_at=str(data.get("captured_at") or datetime.now().astimezone().isoformat()),
            source=str(data.get("source", "manual")),
            snapshot_id=str(data.get("snapshot_id", "")),
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "captured_at": self.captured_at,
            "source": self.source,
            "items": [item.to_dict() for item in self.items],
            "metadata": self.metadata,
        }


@dataclass
class StructureAnalysis:
    snapshot: LayoutSnapshot
    facts: list[dict[str, Any]]
    relations: list[dict[str, Any]]
    groups: list[dict[str, Any]]
    structures: list[dict[str, Any]]
    compression: dict[str, Any]
    gates: dict[str, Any]
    title_candidates: list[dict[str, Any]]
    layout_message: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot": self.snapshot.to_dict(),
            "facts": self.facts,
            "relations": self.relations,
            "groups": self.groups,
            "structures": self.structures,
            "compression": self.compression,
            "gates": self.gates,
            "title_candidates": self.title_candidates,
            "layout_message": self.layout_message,
        }
