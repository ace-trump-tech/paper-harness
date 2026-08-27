import unittest

from paper_harness.adversarial import SelfAdversarialLoop


class AdversarialLoopTest(unittest.TestCase):
    def test_revises_candidates_for_multiple_rounds(self):
        result = SelfAdversarialLoop(max_rounds=3).run(
            [{"candidate_id": "a", "statement": "improve robust evaluation", "novelty_claim": "new metric"}],
            [],
            ["Is the claim falsifiable?"],
        )
        self.assertEqual(len(result["rounds"]), 3)
        self.assertEqual(result["rounds"][0]["candidates"][0]["round"], 1)
        self.assertIn("winner", result)


if __name__ == "__main__":
    unittest.main()
