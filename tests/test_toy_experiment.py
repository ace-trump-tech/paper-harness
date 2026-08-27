import unittest

from paper_harness.experiment import run_toy_experiment


class ToyExperimentTest(unittest.TestCase):
    def test_result_is_reproducible_and_explicitly_limited(self):
        first = run_toy_experiment()
        second = run_toy_experiment()
        self.assertEqual(first, second)
        self.assertTrue(first["reproducible"])
        self.assertIn("synthetic data", first["limitations"])


if __name__ == "__main__":
    unittest.main()
