"""Regression tests for direct saved-preference recall."""
import importlib.util
from pathlib import Path
import unittest

SERVER = Path(__file__).resolve().parents[1] / "server.py"
spec = importlib.util.spec_from_file_location("anshu_phase37_1_server", SERVER)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class SavedPreferenceRecallTests(unittest.TestCase):
    def test_programming_language_preference_is_recalled(self):
        memories = [{"text": "My favourite programming language is Python."}]
        answer = app.find_direct_saved_fact_answer("Which programming language do I like?", memories)
        self.assertIsNotNone(answer)
        self.assertIn("Python", answer)

    def test_disabled_or_empty_memory_does_not_guess(self):
        self.assertIsNone(app.find_direct_saved_fact_answer("Which programming language do I like?", []))

    def test_unrelated_question_does_not_trigger_direct_recall(self):
        memories = [{"text": "My favourite programming language is Python."}]
        self.assertIsNone(app.find_direct_saved_fact_answer("What is the weather?", memories))

if __name__ == "__main__":
    unittest.main()
