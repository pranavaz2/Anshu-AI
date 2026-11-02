import importlib.util
import tempfile
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server.py"
spec = importlib.util.spec_from_file_location("anshu_phase39_server", SERVER)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class Phase39ProjectStatusTruthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        app.DATA_DIR = root
        app.DB_PATH = root / "test.sqlite3"
        app.init_db()
        with app.db_connect() as conn:
            conn.execute(
                "INSERT INTO conversations(role,content,created) VALUES(?,?,?)",
                ("user", "I am building a robot car using ESP32", "2026-10-30T23:00:00")
            )

    def tearDown(self):
        self.tmp.cleanup()

    def test_simulator_false_does_not_claim_physical_status(self):
        answer = app.find_direct_project_status_answer(
            "Did we implement obstacle avoidance?",
            {"autoAvoid": False}
        )
        self.assertIn("can't verify", answer.lower())
        self.assertIn("actual ESP32 robot car", answer)
        self.assertIn("autoAvoid", answer)
        self.assertIn("false", answer)
        self.assertIn("inspect your ESP32 code", answer)

    def test_simulator_true_does_not_claim_hardware_verified(self):
        answer = app.find_direct_project_status_answer(
            "Is obstacle avoidance enabled?",
            {"autoAvoid": True}
        )
        self.assertIn("simulator's `autoAvoid` flag is true", answer)
        self.assertIn("does not verify physical hardware", answer)

    def test_missing_simulator_status_is_reported_as_unknown(self):
        answer = app.find_direct_project_status_answer(
            "Have we built obstacle avoidance?", {}
        )
        self.assertIn("don't have a reliable simulator status", answer)
        self.assertIn("can't verify", answer.lower())

    def test_unrelated_question_is_not_intercepted(self):
        self.assertIsNone(app.find_direct_project_status_answer("What is HTML?", {}))

    def test_non_obstacle_implementation_question_is_not_intercepted(self):
        self.assertIsNone(app.find_direct_project_status_answer("Did we build the camera?", {}))

if __name__ == "__main__":
    unittest.main()
