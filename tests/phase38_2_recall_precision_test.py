"""Phase 38.2 regression tests: specific project recall and follow-up precision."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server.py"
spec = importlib.util.spec_from_file_location("anshu_phase38_2_server", SERVER)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class Phase382RecallPrecisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        app.DATA_DIR = root
        app.DB_PATH = root / "test.sqlite3"
        app.init_db()
        self.add("user", "I am building a robot car using ESP32")
        self.add("assistant", "You could use a camera module like the OV7670 or OV2640.")
        self.add("user", "I want it to have surveillance feature")
        self.add("assistant", "A camera can capture images and video.")
        self.add("user", "I want it to have buzzer")
        self.add("user", "I want a camera in it")
        self.add("user", "I want obstacle avoidance in it")
        self.add("user", "I want light in it")
        self.add("user", "I want it to be intelligent")
        self.add("user", "I want to learn web development")
        self.add("assistant", "Let's start with HTML and CSS.")

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, role, content):
        with app.db_connect() as conn:
            conn.execute(
                "INSERT INTO conversations(role,content,created) VALUES(?,?,?)",
                (role, content, "2026-10-30T23:28:00")
            )

    def test_specific_camera_models_are_attributed_as_suggestions(self):
        answer = app.find_direct_conversation_recall_answer("What camera did we discuss?")
        self.assertIn("OV7670", answer)
        self.assertIn("OV2640", answer)
        self.assertIn("suggestions", answer)
        self.assertIn("did not explicitly confirm", answer)

    def test_other_features_does_not_claim_new_features_were_planned(self):
        answer = app.find_direct_conversation_recall_answer("What other features did we plan?")
        self.assertIn("surveillance", answer)
        self.assertIn("obstacle avoidance", answer)
        self.assertIn("can't find any additional specific features", answer)

    def test_feature_list_uses_user_requested_features(self):
        answer = app.find_direct_conversation_recall_answer(
            "What did we discuss about my ESP32 robot car?"
        )
        for item in ("surveillance", "camera", "buzzer", "obstacle avoidance",
                     "LED lighting", "intelligent behaviour"):
            self.assertIn(item, answer)
        self.assertNotIn("web development", answer)

    def test_unrelated_question_does_not_trigger_project_recall(self):
        self.assertIsNone(app.find_direct_conversation_recall_answer("What is HTML?"))

if __name__ == "__main__":
    unittest.main()
