import importlib.util
import tempfile
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server.py"
spec = importlib.util.spec_from_file_location("anshu_phase38_3_server", SERVER)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class Phase383ProjectAnchorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        app.DATA_DIR = root
        app.DB_PATH = root / "test.sqlite3"
        app.init_db()
        turns = [
            ("user", "I am building a robot car using ESP32"),
            ("assistant", "You can use a camera module like the OV7670 or OV2640."),
            ("user", "I want it to have surveillance feature"),
            ("user", "I want it to have buzzer"),
            ("user", "I want a camera in it"),
            ("user", "I want a obstacle avoidance in it"),
            ("user", "I want light in it"),
            ("user", "I want it to be intelligent"),
            ("user", "i want to learn webdevelopment"),
            ("assistant", "Let's learn HTML and CSS."),
            ("user", "What did we discuss about my ESP32 robot car?"),
            ("user", "What other features did we plan"),
        ]
        for role, content in turns:
            self.add(role, content)

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, role, content):
        with app.db_connect() as conn:
            conn.execute(
                "INSERT INTO conversations(role,content,created) VALUES(?,?,?)",
                (role, content, "2026-10-30T23:28:00")
            )

    def test_camera_models_recalled_from_original_thread(self):
        answer = app.find_direct_conversation_recall_answer("What camera did we discuss?")
        self.assertIn("OV7670", answer)
        self.assertIn("OV2640", answer)
        self.assertIn("suggestions", answer)

    def test_all_six_user_requested_features_recalled(self):
        answer = app.find_direct_conversation_recall_answer(
            "What did we discuss about my ESP32 robot car?"
        )
        for feature in ("surveillance", "buzzer", "camera",
                        "obstacle avoidance", "LED lighting", "intelligent behaviour"):
            self.assertIn(feature, answer)

    def test_followup_does_not_reset_project_anchor(self):
        answer = app.find_direct_conversation_recall_answer("What other features did we plan?")
        for feature in ("surveillance", "buzzer", "camera",
                        "obstacle avoidance", "LED lighting", "intelligent behaviour"):
            self.assertIn(feature, answer)
        self.assertIn("can't find any additional", answer)

    def test_unrelated_question_not_captured(self):
        self.assertIsNone(app.find_direct_conversation_recall_answer("What is HTML?"))

if __name__ == "__main__":
    unittest.main()
