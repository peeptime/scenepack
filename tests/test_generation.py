import json
import tempfile
import unittest
from pathlib import Path

from peepaste.analysis import LayoutAnalyzer
from peepaste.generation import ProjectPackageManager
from peepaste.models import LayoutSnapshot, RectItem
from peepaste.storage import ProjectPackageWriter


class PostGenerationTests(unittest.TestCase):
    def test_accept_title_generates_post_files(self):
        snapshot = LayoutSnapshot(
            source="test",
            items=[
                RectItem(id="a", x=0, y=0, width=200, height=120),
                RectItem(id="b", x=240, y=0, width=200, height=120),
            ],
        )
        analysis = LayoutAnalyzer().analyze(snapshot)
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            ProjectPackageWriter(package).write_record(analysis)
            manager = ProjectPackageManager(package)
            manager.accept_title("Accepted Test Scene")
            result = manager.generate_after_acceptance()
            self.assertTrue(result.files["project"].exists())
            self.assertTrue(result.files["relations"].exists())
            self.assertTrue(result.files["summary"].exists())
            self.assertTrue(result.files["openclaw_prompt"].exists())
            self.assertTrue(result.files["review_sheet"].exists())
            self.assertTrue(result.files["clipboard_bundle"].exists())
            project = json.loads(result.files["project"].read_text(encoding="utf-8"))
            self.assertEqual(project["title"], "Accepted Test Scene")
            prompt = result.files["openclaw_prompt"].read_text(encoding="utf-8")
            self.assertIn("OpenClaw Handoff", prompt)


if __name__ == "__main__":
    unittest.main()
