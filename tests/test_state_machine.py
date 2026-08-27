import unittest

from paper_harness.models import Stage
from paper_harness.state_machine import InvalidTransition, advance


class StateMachineTest(unittest.TestCase):
    def test_valid_transition(self):
        self.assertEqual(advance(Stage.BRIEF, Stage.LITERATURE), Stage.LITERATURE)

    def test_invalid_skip_is_rejected(self):
        with self.assertRaises(InvalidTransition):
            advance(Stage.BRIEF, Stage.EXPERIMENT)


if __name__ == "__main__":
    unittest.main()

