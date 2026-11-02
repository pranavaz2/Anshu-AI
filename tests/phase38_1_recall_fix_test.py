"""Regression tests for Phase 38.1 project-aware deterministic recall."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server.py"
spec = importlib.util.spec_from_file_location("anshu_phase38_1_server", SERVER)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class Phase381RecallFixTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        app.DATA_DIR = root
        app.DB_PATH = root / "test.sqlite3"
        app.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, role, content):
        with app.db_connect() as conn:
            conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)",
                         (role, content, "2026-10-30T23:28:00"))

    def test_robot_project_recall_lists_only_discussed_features(self):
        exchanges = [
            ("user", "I am building a robot car using ESP32"),
            ("assistant", "That sounds like an interesting project."),
            ("user", "i want it to have surveilance feature"),
            ("assistant", "Consider a camera module."),
            ("user", "i want it to have buzzer"),
            ("assistant", "You can add a buzzer."),
            ("user", "i want a camera in it"),
            ("assistant", "A camera module can provide video."),
            ("user", "i want a obstacle avoidance in it"),
            ("assistant", "Obstacle avoidance can be added."),
            ("user", "i want light in it"),
            ("assistant", "Add LEDs."),
            ("user", "i want it to be intelligent"),
            ("assistant", "Add intelligent navigation."),
            ("user", "ok what next"),
            ("assistant", "You can plan a mission."),
            ("user", "i want to learn webdevelopment"),
            ("assistant", "Let's learn HTML and CSS."),
        ]
        for role, content in exchanges:
            self.add(role, content)
        answer = app.find_direct_conversation_recall_answer("What did we discuss about my ESP32 robot car?")
        for expected in ("surveillance", "camera", "buzzer", "obstacle avoidance", "LED lighting", "intelligent behaviour"):
            self.assertIn(expected, answer)
        self.assertNotIn("web development", answer.lower())
        self.assertIn("not confirmation", answer)

    def test_follow_up_inherits_robot_project_from_recent_context(self):
        self.add("user", "What did we discuss about my ESP32 robot car?")
        self.add("assistant", "We discussed camera and obstacle avoidance.")
        self.add("user", "What other features we planned?")
        answer = app.find_direct_conversation_recall_answer("What other features we planned?")
        self.assertIsNotNone(answer)

    def test_unrelated_question_does_not_trigger_recall(self):
        self.add("user", "I want to learn web development")
        self.assertIsNone(app.find_direct_conversation_recall_answer("What is HTML?"))

if __name__ == "__main__":
    unittest.main()
