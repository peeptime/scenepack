import unittest

from peepaste.intelligence import AiRequest, NullAiAdapter


class IntelligenceAdapterTests(unittest.TestCase):
    def test_null_adapter_is_safe_default(self):
        response = NullAiAdapter().complete(AiRequest(purpose="title", layout_summary={}))
        self.assertEqual(response.provider, "none")
        self.assertFalse(response.used_image_reading)
        self.assertEqual(response.token_estimate, 0)


if __name__ == "__main__":
    unittest.main()

