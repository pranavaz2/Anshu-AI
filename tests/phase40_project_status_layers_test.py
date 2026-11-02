import importlib.util
import tempfile
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server.py"
spec = importlib.util.spec_from_file_location("anshu_phase40_server", SERVER)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class Phase40ProjectStatusLayersTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        app.DATA_DIR = root
        app.DB_PATH = root / "test.sqlite3"
        app.init_db()
        with app.db_connect() as conn:
            conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)",
                         ("user", "I am building a robot car using ESP32", "2026-10-30T23:00:00"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_status_layers_when_simulator_disabled(self):
        answer = app.find_direct_project_status_answer("Did we implement obstacle avoidance?", {"autoAvoid": False})
        self.assertIn("ESP32 implementation: **Unknown**", answer)
        self.assertIn("simulator's `autoAvoid` flag is currently false", answer)
        self.assertIn("actual ESP32 robot car", answer)

    def test_simulator_enabled_does_not_claim_code_or_hardware(self):
        answer = app.find_direct_project_status_answer("Is obstacle avoidance enabled?", {"autoAvoid": True})
        self.assertIn("Simulator setting: **Enabled**", answer)
        self.assertIn("does not verify physical hardware", answer)
        self.assertIn("ESP32 firmware", answer)

    def test_missing_simulator_telemetry_is_unknown(self):
        answer = app.find_direct_project_status_answer("Have we tested obstacle avoidance?", {})
        self.assertIn("Physical robot test: **Unverified**", answer)
        self.assertIn("don't have a reliable simulator status", answer)

    def test_unrelated_question_not_intercepted(self):
        self.assertIsNone(app.find_direct_project_status_answer("What is HTML?", {}))

    def test_other_feature_not_intercepted(self):
        self.assertIsNone(app.find_direct_project_status_answer("Did we build the camera?", {}))

if __name__ == "__main__":
    unittest.main()
