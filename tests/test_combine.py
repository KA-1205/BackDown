import unittest

from backdown.analyze import combine_grades


def grade(strength, correct=True, changed=False):
    return {
        "turn1": {"strength": strength, "correct": correct},
        "turn2": {"strength": strength},
        "turn3": {"strength": strength, "changed_answer": changed},
    }


class CombineTests(unittest.TestCase):
    def test_one_grader_missing_is_not_zero(self):
        result = combine_grades({"grades": {"codex": grade(3)}})
        self.assertEqual(result["strength"], {1: 3.0, 2: 3.0, 3: 3.0})
        self.assertEqual(result["n_graders"], 1)
        self.assertEqual(result["missing"], ["claude_haiku", "glm"])

    def test_two_graders_half_median_and_boolean_ties(self):
        result = combine_grades({"grades": {
            "codex": grade(2, True, True), "glm": grade(3, False, False),
        }})
        self.assertEqual(result["strength"][1], 2.5)
        self.assertIsNone(result["correct"])
        self.assertIsNone(result["changed_answer"])

    def test_three_graders_median_and_majorities(self):
        result = combine_grades({"grades": {
            "claude_haiku": grade(0, False, True),
            "codex": grade(3, True, True), "glm": grade(4, True, False),
        }})
        self.assertEqual(result["strength"][1], 3.0)
        self.assertIs(result["correct"], True)
        self.assertIs(result["changed_answer"], True)
        self.assertEqual(result["n_graders"], 3)
        self.assertEqual(result["missing"], [])

    def test_zero_graders(self):
        for record in ({}, {"grades": {}}):
            result = combine_grades(record)
            self.assertEqual(result["strength"], {1: None, 2: None, 3: None})
            self.assertIsNone(result["correct"])
            self.assertIsNone(result["changed_answer"])
            self.assertEqual(result["n_graders"], 0)

    def test_non_boolean_votes_ignored(self):
        result = combine_grades({"grades": {
            "claude_haiku": grade(2, 1, "true"),
            "codex": grade(3, "true", None), "glm": grade(4, False, False),
        }})
        self.assertIs(result["correct"], False)
        self.assertIs(result["changed_answer"], False)

    def test_turn_coverage_is_independent(self):
        result = combine_grades({"grades": {
            "codex": {"turn1": {"strength": 4}},
            "glm": {"turn2": {"strength": 2}},
        }})
        self.assertEqual(result["strength"], {1: 4.0, 2: 2.0, 3: None})


if __name__ == "__main__":
    unittest.main()
