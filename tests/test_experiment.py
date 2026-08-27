import unittest

from paper_harness.experiment import ExperimentRunner
from paper_harness.models import ExperimentSpec


class ExperimentTest(unittest.TestCase):
    def test_dry_run_does_not_execute(self):
        result = ExperimentRunner().run(ExperimentSpec("demo", ["definitely-not-run"], dry_run=True))
        self.assertEqual(result["status"], "planned")


if __name__ == "__main__":
    unittest.main()

