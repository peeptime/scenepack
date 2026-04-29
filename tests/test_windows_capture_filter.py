import unittest

from peepaste.capture.windows import _is_snipaste_paster


class WindowsCaptureFilterTests(unittest.TestCase):
    def test_detects_snipaste_paster_window(self):
        self.assertTrue(_is_snipaste_paster("Paster - Snipaste", "Snipaste.exe", "Qt624QWindowToolSaveBits"))

    def test_rejects_snipaste_preferences_window(self):
        self.assertFalse(_is_snipaste_paster("Snipaste Preferences", "Snipaste.exe", "Qt624QWindowIcon"))


if __name__ == "__main__":
    unittest.main()

