import unittest

from peepaste.analysis import LayoutAnalyzer
from peepaste.models import LayoutSnapshot, RectItem


class LayoutAnalyzerTests(unittest.TestCase):
    def test_balanced_set_is_detected_for_four_corners(self):
        snapshot = LayoutSnapshot(
            source="test",
            items=[
                RectItem(id="a", x=0, y=0, width=100, height=100),
                RectItem(id="b", x=300, y=0, width=100, height=100),
                RectItem(id="c", x=0, y=300, width=100, height=100),
                RectItem(id="d", x=300, y=300, width=100, height=100),
            ],
        )
        analysis = LayoutAnalyzer().analyze(snapshot)
        structure_types = {structure["type"] for structure in analysis.structures}
        self.assertIn("balanced_set", structure_types)

    def test_small_isolated_item_requires_image_reading_gate(self):
        snapshot = LayoutSnapshot(
            source="test",
            items=[
                RectItem(id="main", x=0, y=0, width=500, height=320),
                RectItem(id="small", x=1200, y=800, width=80, height=60),
            ],
        )
        analysis = LayoutAnalyzer().analyze(snapshot)
        self.assertTrue(analysis.gates["needs_image_reading"])
        self.assertGreaterEqual(len(analysis.groups), 2)


if __name__ == "__main__":
    unittest.main()

