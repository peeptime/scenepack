import tempfile
import unittest
from pathlib import Path

from peepaste.settings import AppSettings


class SettingsTests(unittest.TestCase):
    def test_settings_round_trip(self):
        settings = AppSettings()
        settings.storage_root = "custom-projects"
        settings.appearance.language = "zh"
        settings.ai.enabled = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            settings.save(path)
            loaded = AppSettings.load(path)
            self.assertEqual(loaded.storage_root, "custom-projects")
            self.assertEqual(loaded.appearance.language, "zh")
            self.assertTrue(loaded.ai.enabled)

    def test_expands_environment_variables_in_storage_root(self):
        loaded = AppSettings.from_mapping({"storage_root": r"%USERPROFILE%\PeepasteTest"})
        self.assertNotIn("%USERPROFILE%", loaded.storage_root)


if __name__ == "__main__":
    unittest.main()
