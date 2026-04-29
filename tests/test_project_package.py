import json
import tempfile
import unittest
from pathlib import Path

from peepaste.analysis import LayoutAnalyzer
from peepaste.models import LayoutSnapshot, RectItem
from peepaste.storage import ProjectPackageWriter


class ProjectPackageWriterTests(unittest.TestCase):
    def test_writes_record_state_and_message(self):
        snapshot = LayoutSnapshot(source="test", items=[RectItem(id="a", x=10, y=20, width=100, height=80)])
        analysis = LayoutAnalyzer().analyze(snapshot)
        with tempfile.TemporaryDirectory() as tmp:
            paths = ProjectPackageWriter(Path(tmp)).write_record(analysis)
            self.assertTrue(paths["layout"].exists())
            self.assertTrue(paths["message"].exists())
            self.assertTrue(paths["state"].exists())
            state = json.loads(paths["state"].read_text(encoding="utf-8"))
            self.assertEqual(state["mode"], "mode_1_structure")


if __name__ == "__main__":
    unittest.main()

