import unittest

import setting
import utils


class UtilsTests(unittest.TestCase):
    def test_scale_factor_at_default_size(self) -> None:
        self.assertAlmostEqual(
            utils.scale_factor(setting.DEFAULT_WIDTH, setting.DEFAULT_HEIGHT),
            1.0,
        )

    def test_scale_factor_clamped(self) -> None:
        tiny = utils.scale_factor(100, 100)
        huge = utils.scale_factor(5000, 5000)
        self.assertGreaterEqual(tiny, 0.65)
        self.assertLessEqual(huge, 2.0)

    def test_scaled_size_minimum_one(self) -> None:
        self.assertEqual(utils.scaled_size(10, 0.1), 1)

    def test_font_size_from_box(self) -> None:
        self.assertEqual(utils.font_size_from_box(0, 0, 0.5), 8)
        self.assertEqual(utils.font_size_from_box(100, 80, 0.5), 40)
        self.assertEqual(utils.font_size_from_box(100, 80, 0.5, max_size=30), 30)


if __name__ == "__main__":
    unittest.main()
