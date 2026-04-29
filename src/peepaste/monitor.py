from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Callable

from peepaste.models import LayoutSnapshot, RectItem


@dataclass
class SceneChange:
    change_type: str
    item_id: str
    before: dict | None = None
    after: dict | None = None


@dataclass
class MonitorTick:
    snapshot: LayoutSnapshot
    fingerprint: str
    stable_ticks: int
    changes: list[SceneChange]
    is_stable: bool


class SceneMonitor:
    def __init__(self, capture: Callable[[], LayoutSnapshot], stable_ticks_required: int = 2):
        self.capture = capture
        self.stable_ticks_required = max(1, stable_ticks_required)
        self.previous: LayoutSnapshot | None = None
        self.previous_fingerprint = ""
        self.stable_ticks = 0

    def tick(self) -> MonitorTick:
        snapshot = self.capture()
        fingerprint = layout_fingerprint(snapshot)
        changes = diff_snapshots(self.previous, snapshot)
        if fingerprint == self.previous_fingerprint:
            self.stable_ticks += 1
        else:
            self.stable_ticks = 1
        self.previous = snapshot
        self.previous_fingerprint = fingerprint
        return MonitorTick(
            snapshot=snapshot,
            fingerprint=fingerprint,
            stable_ticks=self.stable_ticks,
            changes=changes,
            is_stable=self.stable_ticks >= self.stable_ticks_required,
        )

    def run(self, iterations: int, interval_seconds: float) -> list[MonitorTick]:
        ticks = []
        remaining = iterations
        while remaining != 0:
            ticks.append(self.tick())
            if remaining > 0:
                remaining -= 1
            if remaining != 0:
                time.sleep(interval_seconds)
        return ticks


def layout_fingerprint(snapshot: LayoutSnapshot) -> str:
    payload = [
        {
            "source_ref": item.source_ref,
            "title": item.title,
            "process": item.process,
            "class_name": item.class_name,
            "x": round(item.x),
            "y": round(item.y),
            "width": round(item.width),
            "height": round(item.height),
        }
        for item in sorted(snapshot.items, key=lambda current: (current.source_ref, current.id))
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def diff_snapshots(before: LayoutSnapshot | None, after: LayoutSnapshot) -> list[SceneChange]:
    if before is None:
        return [SceneChange("added", item.id, after=_item_state(item)) for item in after.items]
    before_map = {_key(item): item for item in before.items}
    after_map = {_key(item): item for item in after.items}
    changes: list[SceneChange] = []
    for key, item in after_map.items():
        if key not in before_map:
            changes.append(SceneChange("added", item.id, after=_item_state(item)))
            continue
        previous = before_map[key]
        moved = round(previous.x) != round(item.x) or round(previous.y) != round(item.y)
        resized = round(previous.width) != round(item.width) or round(previous.height) != round(item.height)
        if moved:
            changes.append(SceneChange("moved", item.id, before=_item_state(previous), after=_item_state(item)))
        if resized:
            changes.append(SceneChange("resized", item.id, before=_item_state(previous), after=_item_state(item)))
    for key, item in before_map.items():
        if key not in after_map:
            changes.append(SceneChange("removed", item.id, before=_item_state(item)))
    return changes


def _key(item: RectItem) -> str:
    return item.source_ref or item.id


def _item_state(item: RectItem) -> dict:
    return {
        "id": item.id,
        "source_ref": item.source_ref,
        "x": item.x,
        "y": item.y,
        "width": item.width,
        "height": item.height,
    }

