import importlib.util
import tempfile
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server.py"
spec = importlib.util.spec_from_file_location("anshu_phase41_server", SERVER)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class Phase41ProjectStatusIntentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        app.DATA_DIR = root
        app.DB_PATH = root / "test.sqlite3"
        app.init_db()
        with app.db_connect() as conn:
            conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)",
                         ("user", "I am building an ESP32 robot car", "2026-10-31T10:00:00"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_implementation_question_is_firmware_focused(self):
        answer = app.find_direct_project_status_answer("Did we implement obstacle avoidance?", {"autoAvoid": False})
        self.assertIn("ESP32 implementation: **Unknown**", answer)
        self.assertIn("simulator is disabled", answer)
        self.assertNotIn("Planned:", answer)

    def test_enabled_question_is_simulator_focused(self):
        answer = app.find_direct_project_status_answer("Is obstacle avoidance enabled?", {"autoAvoid": False})
        self.assertIn("Simulator setting: **Disabled**", answer)
        self.assertIn("does not tell me whether", answer)
        self.assertNotIn("Physical robot test:", answer)

    def test_enabled_true_is_not_physical_confirmation(self):
        answer = app.find_direct_project_status_answer("Is obstacle avoidance enabled?", {"autoAvoid": True})
        self.assertIn("Simulator setting: **Enabled**", answer)
        self.assertIn("physical robot works", answer)

    def test_physical_test_question_is_test_focused(self):
        answer = app.find_direct_project_status_answer("Have we tested obstacle avoidance on the physical robot?", {"autoAvoid": False})
        self.assertIn("Physical robot test: **Unverified**", answer)
        self.assertIn("not proof of a physical test", answer)
        self.assertNotIn("ESP32 implementation:", answer)

    def test_missing_telemetry_stays_unknown(self):
        answer = app.find_direct_project_status_answer("Is obstacle avoidance enabled?", {})
        self.assertIn("Simulator setting: **Unknown**", answer)

    def test_non_obstacle_question_not_intercepted(self):
        self.assertIsNone(app.find_direct_project_status_answer("Did we implement camera support?", {}))

if __name__ == "__main__":
    unittest.main()
