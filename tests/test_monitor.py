import unittest

from peepaste.models import LayoutSnapshot, RectItem
from peepaste.monitor import SceneMonitor, diff_snapshots


class SceneMonitorTests(unittest.TestCase):
    def test_diff_detects_moved_and_resized_items(self):
        before = LayoutSnapshot(items=[RectItem(id="a", source_ref="1", x=0, y=0, width=100, height=100)])
        after = LayoutSnapshot(items=[RectItem(id="a", source_ref="1", x=20, y=0, width=120, height=100)])
        changes = diff_snapshots(before, after)
        self.assertEqual({change.change_type for change in changes}, {"moved", "resized"})

    def test_monitor_marks_stable_after_required_ticks(self):
        snapshot = LayoutSnapshot(items=[RectItem(id="a", source_ref="1", x=0, y=0, width=100, height=100)])
        monitor = SceneMonitor(lambda: snapshot, stable_ticks_required=2)
        first = monitor.tick()
        second = monitor.tick()
        self.assertFalse(first.is_stable)
        self.assertTrue(second.is_stable)


if __name__ == "__main__":
    unittest.main()

