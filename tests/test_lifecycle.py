import tempfile
import unittest
from pathlib import Path

from peepaste.lifecycle import SceneLifecycle, ScenePhase


class SceneLifecycleTests(unittest.TestCase):
    def test_capture_confirm_generate_handoff_flow(self):
        lifecycle = SceneLifecycle()
        self.assertEqual(lifecycle.phase, ScenePhase.SILENT_CAPTURE)

        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)
            lifecycle.captured(package)
            self.assertEqual(lifecycle.phase, ScenePhase.NEEDS_CONFIRMATION)
            self.assertFalse(lifecycle.can_generate)

            lifecycle.title_selected("Research Board")
            self.assertTrue(lifecycle.can_generate)

            lifecycle.generated({"openclaw_prompt": package / "openclaw_prompt.md"})
            self.assertEqual(lifecycle.phase, ScenePhase.READY_TO_HANDOFF)
            self.assertTrue(lifecycle.can_handoff)

            lifecycle.handed_off()
            self.assertEqual(lifecycle.phase, ScenePhase.HANDED_OFF)


if __name__ == "__main__":
    unittest.main()
