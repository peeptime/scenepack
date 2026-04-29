from __future__ import annotations

import math
from statistics import median
from typing import Iterable

from peepaste.models import LayoutSnapshot, RectItem, StructureAnalysis


class LayoutAnalyzer:
    """Mode 1 structural analyzer.

    It does not read image content. It only converts layout facts into a rich
    internal structure pool that can later guide title matching or AI mode.
    """

    def analyze(self, snapshot: LayoutSnapshot) -> StructureAnalysis:
        items = [item for item in snapshot.items if item.width > 0 and item.height > 0]
        facts = self._facts(items)
        relations = self._relations(items)
        groups = self._groups(items, relations)
        structures = self._structures(items, groups)
        compression = self._compression(items, groups, structures)
        gates = self._gates(items, groups, structures, compression)
        title_candidates = self._title_candidates(snapshot, groups, structures, gates)
        layout_message = self._layout_message(items, groups, structures, gates)
        cleaned_snapshot = LayoutSnapshot(
            items=items,
            captured_at=snapshot.captured_at,
            source=snapshot.source,
            snapshot_id=snapshot.snapshot_id,
            metadata=snapshot.metadata,
        )
        return StructureAnalysis(
            snapshot=cleaned_snapshot,
            facts=facts,
            relations=relations,
            groups=groups,
            structures=structures,
            compression=compression,
            gates=gates,
            title_candidates=title_candidates,
            layout_message=layout_message,
        )

    def _facts(self, items: list[RectItem]) -> list[dict]:
        if not items:
            return []
        min_x, min_y, max_x, max_y = self._bounds(items)
        total_area = max(1.0, (max_x - min_x) * (max_y - min_y))
        areas = [item.area for item in items]
        area_med = median(areas) if areas else 0
        density_radius = max(80.0, math.sqrt(area_med) * 1.8) if area_med else 120.0
        facts = []
        for item in items:
            nearest_distance = self._nearest_distance(item, items)
            isolation_score = min(1.0, nearest_distance / max(1.0, density_radius * 2.5))
            facts.append(
                {
                    "item_id": item.id,
                    "type": "spatial_metrics",
                    "box": {"x": item.x, "y": item.y, "width": item.width, "height": item.height},
                    "area_weight": round(item.area / total_area, 5),
                    "scale_tier": self._scale_tier(item.area, areas),
                    "screen_zone": self._screen_zone(item, min_x, min_y, max_x, max_y),
                    "nearest_distance": round(nearest_distance, 2),
                    "local_density": self._local_density(item, items, density_radius),
                    "isolation_score": round(isolation_score, 3),
                    "whitespace_ratio": round(nearest_distance / max(1.0, math.sqrt(item.area)), 3),
                }
            )
        return facts

    def _relations(self, items: list[RectItem]) -> list[dict]:
        relations: list[dict] = []
        if len(items) < 2:
            return relations
        typical_diag = median([math.hypot(item.width, item.height) for item in items])
        near_threshold = max(80.0, typical_diag * 0.75)
        align_tolerance = max(16.0, median([item.height for item in items]) * 0.18)
        for index, left in enumerate(items):
            distances = []
            for right in items[index + 1 :]:
                dist = self._edge_distance(left, right)
                distances.append((dist, right))
                relations.extend(self._pair_relations(left, right, dist, near_threshold, align_tolerance))
            for dist, neighbor in sorted(distances, key=lambda pair: pair[0])[:3]:
                relations.append(
                    {
                        "type": "nearest_neighbor",
                        "from": left.id,
                        "to": neighbor.id,
                        "confidence": self._confidence_from_distance(dist, near_threshold),
                    }
                )
        return self._dedupe_relations(relations)

    def _pair_relations(
        self,
        left: RectItem,
        right: RectItem,
        dist: float,
        near_threshold: float,
        align_tolerance: float,
    ) -> list[dict]:
        rels = []
        if dist <= near_threshold:
            rels.append({"type": "near", "from": left.id, "to": right.id, "confidence": self._confidence_from_distance(dist, near_threshold)})
        if self._overlap_area(left, right) > 0:
            rels.append({"type": "overlap", "from": left.id, "to": right.id, "confidence": 0.95})
        if abs(left.y - right.y) <= align_tolerance:
            rels.append({"type": "aligned_top", "from": left.id, "to": right.id, "confidence": 0.78})
        if abs(left.center[1] - right.center[1]) <= align_tolerance:
            rels.append({"type": "aligned_center_y", "from": left.id, "to": right.id, "confidence": 0.82})
        if abs(left.x - right.x) <= align_tolerance:
            rels.append({"type": "aligned_left", "from": left.id, "to": right.id, "confidence": 0.78})
        if abs(left.center[0] - right.center[0]) <= align_tolerance:
            rels.append({"type": "aligned_center_x", "from": left.id, "to": right.id, "confidence": 0.82})
        area_ratio = min(left.area, right.area) / max(left.area, right.area)
        if area_ratio >= 0.72:
            rels.append({"type": "similar_size", "from": left.id, "to": right.id, "confidence": round(area_ratio, 3)})
        if left.right <= right.x:
            rels.append({"type": "left_of", "from": left.id, "to": right.id, "confidence": 0.7})
        elif right.right <= left.x:
            rels.append({"type": "right_of", "from": left.id, "to": right.id, "confidence": 0.7})
        if left.bottom <= right.y:
            rels.append({"type": "above", "from": left.id, "to": right.id, "confidence": 0.7})
        elif right.bottom <= left.y:
            rels.append({"type": "below", "from": left.id, "to": right.id, "confidence": 0.7})
        return rels

    def _groups(self, items: list[RectItem], relations: list[dict]) -> list[dict]:
        if not items:
            return []
        graph: dict[str, set[str]] = {item.id: set() for item in items}
        for relation in relations:
            if relation["type"] in {"near", "overlap", "nearest_neighbor"} and relation.get("confidence", 0) >= 0.45:
                graph[relation["from"]].add(relation["to"])
                graph[relation["to"]].add(relation["from"])
        components = self._components(graph)
        groups = []
        item_map = {item.id: item for item in items}
        for index, component in enumerate(components, start=1):
            group_items = [item_map[item_id] for item_id in component]
            group_type = "cluster" if len(group_items) > 1 else "isolated_item"
            groups.append(
                {
                    "id": f"group_{index:02d}",
                    "type": group_type,
                    "items": sorted(component),
                    "size": len(group_items),
                    "bounds": self._group_bounds(group_items),
                    "density": self._group_density(group_items),
                    "representative_item": max(group_items, key=lambda item: item.area).id,
                }
            )
        return sorted(groups, key=lambda group: (-group["size"], group["id"]))

    def _structures(self, items: list[RectItem], groups: list[dict]) -> list[dict]:
        structures: list[dict] = []
        if not items:
            return structures
        rows = self._axis_sets(items, "y")
        cols = self._axis_sets(items, "x")
        for index, row in enumerate(rows, start=1):
            if len(row) >= 2:
                structures.append({"type": "row", "id": f"row_{index:02d}", "items": [item.id for item in row], "confidence": 0.74})
        for index, col in enumerate(cols, start=1):
            if len(col) >= 2:
                structures.append({"type": "column", "id": f"column_{index:02d}", "items": [item.id for item in col], "confidence": 0.74})
        if len(rows) >= 2 and len(cols) >= 2 and len(items) >= 4:
            coverage = sum(1 for row in rows if len(row) >= 2) + sum(1 for col in cols if len(col) >= 2)
            if coverage >= 4:
                structures.append({"type": "grid_candidate", "items": [item.id for item in items], "confidence": min(0.86, 0.45 + coverage / 10)})
        balanced = self._balanced_set(items)
        if balanced:
            structures.append(balanced)
        anchor = self._attention_anchor(items)
        if anchor:
            structures.append(anchor)
        if len(groups) >= 2:
            structures.append(
                {
                    "type": "multi_zone",
                    "groups": [group["id"] for group in groups],
                    "confidence": min(0.9, 0.48 + len(groups) / 10),
                }
            )
        for group in groups:
            if group["type"] == "isolated_item":
                structures.append({"type": "boundary_or_pending_candidate", "items": group["items"], "confidence": 0.52})
        return structures

    def _compression(self, items: list[RectItem], groups: list[dict], structures: list[dict]) -> dict:
        item_count = len(items)
        group_count = len(groups)
        structure_count = len(structures)
        entropy = self._structure_entropy(items, groups)
        return {
            "item_count": item_count,
            "group_count": group_count,
            "structure_count": structure_count,
            "compression_gain": round(1 - (max(1, group_count) / max(1, item_count)), 3),
            "structure_entropy": entropy,
            "recommended_detail": "region_summary" if item_count >= 20 else "item_level",
            "expand_policy": "expand_on_demand" if item_count >= 20 or entropy >= 0.65 else "safe_to_expand",
        }

    def _gates(self, items: list[RectItem], groups: list[dict], structures: list[dict], compression: dict) -> dict:
        item_count = len(items)
        title_confidence = 0.25
        if item_count:
            title_confidence += min(0.22, len(groups) * 0.04)
            title_confidence += min(0.18, len(structures) * 0.025)
            title_confidence -= min(0.22, compression["structure_entropy"] * 0.22)
        title_confidence = max(0.0, min(0.88, title_confidence))
        semantic_risk = "high" if compression["structure_entropy"] >= 0.68 else "medium" if compression["structure_entropy"] >= 0.42 else "low"
        return {
            "title_candidate_allowed": bool(items),
            "title_confidence": round(title_confidence, 3),
            "needs_title_confirmation": title_confidence < 0.62,
            "silent_generation_ready": title_confidence >= 0.7 and semantic_risk == "low",
            "semantic_risk": semantic_risk,
            "mixed_context_warning": semantic_risk == "high" or len(groups) >= 4,
            "should_not_infer": not items or semantic_risk == "high",
            "needs_image_reading": title_confidence < 0.55 or semantic_risk != "low",
        }

    def _title_candidates(self, snapshot: LayoutSnapshot, groups: list[dict], structures: list[dict], gates: dict) -> list[dict]:
        if not gates["title_candidate_allowed"]:
            return []
        date_part = snapshot.captured_at[:10] if snapshot.captured_at else "untitled"
        names = []
        structure_types = {structure["type"] for structure in structures}
        if "grid_candidate" in structure_types:
            names.append(("Grid Scene", 0.58))
        if "multi_zone" in structure_types:
            names.append((f"{len(groups)}-Zone Visual Scene", 0.54))
        if "attention_anchor" in structure_types:
            names.append(("Anchor-Based Visual Scene", 0.52))
        if not names:
            names.append(("Visual Working Scene", 0.42))
        names.append((f"ScenePack Scene {date_part}", 0.36))
        return [{"title": title, "confidence": round(min(conf, gates["title_confidence"]), 3), "status": "candidate"} for title, conf in names]

    def _layout_message(self, items: list[RectItem], groups: list[dict], structures: list[dict], gates: dict) -> dict[str, str]:
        structure_names = sorted({structure["type"] for structure in structures})[:5]
        structure_text = ", ".join(structure_names) if structure_names else "no strong structure"
        zh_structure_text = _translate_structure_text(structure_text)
        zh_risk = {"low": "低", "medium": "中", "high": "高"}.get(gates["semantic_risk"], gates["semantic_risk"])
        en = (
            f"Captured {len(items)} items. The scene has {len(groups)} structural groups and "
            f"{structure_text}. Title confidence is {gates['title_confidence']:.2f}; "
            f"semantic risk is {gates['semantic_risk']}."
        )
        zh = (
            f"已捕获 {len(items)} 个项目。当前场景包含 {len(groups)} 个结构分组，"
            f"主要结构为 {zh_structure_text}。标题置信度 {gates['title_confidence']:.2f}，"
            f"语义风险为{zh_risk}。"
        )
        return {"en": en, "zh": zh}

    def _bounds(self, items: list[RectItem]) -> tuple[float, float, float, float]:
        return (min(item.x for item in items), min(item.y for item in items), max(item.right for item in items), max(item.bottom for item in items))

    def _group_bounds(self, items: list[RectItem]) -> dict:
        min_x, min_y, max_x, max_y = self._bounds(items)
        return {"x": min_x, "y": min_y, "width": max_x - min_x, "height": max_y - min_y}

    def _group_density(self, items: list[RectItem]) -> float:
        if not items:
            return 0.0
        bounds = self._group_bounds(items)
        area = max(1.0, bounds["width"] * bounds["height"])
        return round(sum(item.area for item in items) / area, 3)

    def _screen_zone(self, item: RectItem, min_x: float, min_y: float, max_x: float, max_y: float) -> str:
        cx, cy = item.center
        width = max(1.0, max_x - min_x)
        height = max(1.0, max_y - min_y)
        x_band = "left" if cx < min_x + width / 3 else "right" if cx > min_x + width * 2 / 3 else "center"
        y_band = "top" if cy < min_y + height / 3 else "bottom" if cy > min_y + height * 2 / 3 else "middle"
        return f"{y_band}_{x_band}"

    def _scale_tier(self, area: float, areas: list[float]) -> str:
        sorted_areas = sorted(areas)
        if len(sorted_areas) < 4:
            ratio = area / max(sorted_areas)
            return "large" if ratio >= 0.72 else "medium" if ratio >= 0.38 else "small"
        q1 = sorted_areas[len(sorted_areas) // 4]
        q3 = sorted_areas[(len(sorted_areas) * 3) // 4]
        if area <= q1 * 0.75:
            return "tiny"
        if area <= q1:
            return "small"
        if area >= q3 * 1.35:
            return "large"
        return "medium"

    def _edge_distance(self, left: RectItem, right: RectItem) -> float:
        dx = max(left.x - right.right, right.x - left.right, 0)
        dy = max(left.y - right.bottom, right.y - left.bottom, 0)
        return math.hypot(dx, dy)

    def _nearest_distance(self, item: RectItem, items: list[RectItem]) -> float:
        others = [self._edge_distance(item, other) for other in items if other.id != item.id]
        return min(others) if others else 0.0

    def _local_density(self, item: RectItem, items: list[RectItem], radius: float) -> int:
        return sum(1 for other in items if other.id != item.id and self._edge_distance(item, other) <= radius)

    def _overlap_area(self, left: RectItem, right: RectItem) -> float:
        x_overlap = max(0.0, min(left.right, right.right) - max(left.x, right.x))
        y_overlap = max(0.0, min(left.bottom, right.bottom) - max(left.y, right.y))
        return x_overlap * y_overlap

    def _confidence_from_distance(self, distance: float, threshold: float) -> float:
        return round(max(0.35, min(0.95, 1.0 - distance / max(1.0, threshold * 1.5))), 3)

    def _dedupe_relations(self, relations: list[dict]) -> list[dict]:
        seen = set()
        result = []
        for relation in relations:
            key = (relation["type"], relation["from"], relation["to"])
            if key not in seen:
                seen.add(key)
                result.append(relation)
        return result

    def _components(self, graph: dict[str, set[str]]) -> list[set[str]]:
        seen = set()
        components = []
        for node in graph:
            if node in seen:
                continue
            stack = [node]
            component = set()
            while stack:
                current = stack.pop()
                if current in seen:
                    continue
                seen.add(current)
                component.add(current)
                stack.extend(graph[current] - seen)
            components.append(component)
        return components

    def _axis_sets(self, items: list[RectItem], axis: str) -> list[list[RectItem]]:
        values = [(item.center[1] if axis == "y" else item.center[0], item) for item in items]
        tolerance = max(28.0, median([item.height if axis == "y" else item.width for item in items]) * 0.35)
        groups: list[list[RectItem]] = []
        for _, item in sorted(values, key=lambda value: value[0]):
            placed = False
            for group in groups:
                base = median([member.center[1] if axis == "y" else member.center[0] for member in group])
                current = item.center[1] if axis == "y" else item.center[0]
                if abs(current - base) <= tolerance:
                    group.append(item)
                    placed = True
                    break
            if not placed:
                groups.append([item])
        return [sorted(group, key=lambda member: member.x if axis == "y" else member.y) for group in groups]

    def _balanced_set(self, items: list[RectItem]) -> dict | None:
        if len(items) < 4:
            return None
        areas = [item.area for item in items]
        if min(areas) / max(areas) < 0.68:
            return None
        min_x, min_y, max_x, max_y = self._bounds(items)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        quadrants = set()
        for item in items:
            cx, cy = item.center
            quadrants.add(("left" if cx <= center_x else "right", "top" if cy <= center_y else "bottom"))
        if len(quadrants) >= 4:
            return {"type": "balanced_set", "items": [item.id for item in items], "confidence": 0.72}
        return None

    def _attention_anchor(self, items: list[RectItem]) -> dict | None:
        if len(items) < 3:
            return None
        largest = max(items, key=lambda item: item.area)
        area_ratio = largest.area / max(1.0, median([item.area for item in items]))
        if area_ratio >= 1.8:
            return {"type": "attention_anchor", "items": [largest.id], "confidence": min(0.88, 0.45 + area_ratio / 8)}
        return None

    def _structure_entropy(self, items: list[RectItem], groups: list[dict]) -> float:
        if not items:
            return 1.0
        group_sizes = [group["size"] for group in groups]
        total = sum(group_sizes)
        if total <= 0:
            return 1.0
        entropy = -sum((size / total) * math.log(size / total, 2) for size in group_sizes if size)
        max_entropy = math.log(max(1, len(group_sizes)), 2) or 1.0
        return round(min(1.0, entropy / max_entropy), 3)


def _translate_structure_text(value: str) -> str:
    if value == "no strong structure":
        return "暂无强结构"
    names = {
        "attention_anchor": "注意力锚点",
        "balanced_set": "平衡集合",
        "boundary_or_pending_candidate": "边界/待确认项",
        "column": "列结构",
        "grid_candidate": "网格候选",
        "multi_zone": "多区域结构",
        "row": "行结构",
    }
    return "、".join(names.get(part.strip(), part.strip()) for part in value.split(",") if part.strip())
