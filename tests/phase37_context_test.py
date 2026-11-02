"""Focused tests for Phase 37 local context helpers."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server.py"
spec = importlib.util.spec_from_file_location("anshu_phase37_server", SERVER)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class Phase37ContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        app.DATA_DIR = root
        app.DATA_DIR.mkdir(exist_ok=True)
        app.DB_PATH = root / "test.sqlite3"
        app.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def test_memory_context_setting_round_trip(self):
        app.write_store("context_settings.json", {"use_memories": False})
        self.assertFalse(app.read_settings("context_settings.json", {"use_memories": True})["use_memories"])

    def test_summary_is_bounded_and_created_from_old_turns(self):
        with app.db_connect() as conn:
            for i in range(24):
                conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)",
                             ("user" if i % 2 == 0 else "assistant", f"Older local context item {i}", "2026-10-30"))
        app.refresh_conversation_summary()
        with app.db_connect() as conn:
            row = conn.execute("SELECT summary FROM conversation_summary WHERE id=1").fetchone()
        self.assertIsNotNone(row)
        self.assertLessEqual(len(row[0]), 1800)
        self.assertIn("Older local context item", row[0])

    def test_short_conversations_do_not_create_summary(self):
        with app.db_connect() as conn:
            for i in range(8):
                conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)",
                             ("user", f"Short item {i}", "2026-10-30"))
        app.refresh_conversation_summary()
        with app.db_connect() as conn:
            row = conn.execute("SELECT summary FROM conversation_summary WHERE id=1").fetchone()
        self.assertIsNone(row)

if __name__ == "__main__":
    unittest.main()
