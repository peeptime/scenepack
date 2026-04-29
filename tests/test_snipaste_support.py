import unittest

from peepaste.capture.snipaste import is_supported_version, parse_version_from_path


class SnipasteSupportTests(unittest.TestCase):
    def test_supported_version_range(self):
        self.assertFalse(is_supported_version("2.10.6"))
        self.assertTrue(is_supported_version("2.10.8"))
        self.assertTrue(is_supported_version("2.11.3"))
        self.assertFalse(is_supported_version("2.11.4"))

    def test_parse_version_from_path(self):
        self.assertEqual(parse_version_from_path(r"Z:\2023\Snipaste-2.10.8-x64\Snipaste.exe"), "2.10.8")


if __name__ == "__main__":
    unittest.main()

