"""Tests for Phase 38 relevant local conversation recall."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server.py"
spec = importlib.util.spec_from_file_location("anshu_phase38_server", SERVER)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)

class Phase38ConversationRecallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        app.DATA_DIR = root
        app.DB_PATH = root / "test.sqlite3"
        app.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def test_recalls_relevant_older_user_and_assistant_turn(self):
        with app.db_connect() as conn:
            conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)", ("user", "I am building a robot car using ESP32 and L298N motor driver.", "2026-10-30"))
            conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)", ("assistant", "We discussed wiring the motors through the driver.", "2026-10-30"))
            for i in range(14):
                conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)", ("user" if i % 2 == 0 else "assistant", f"Unrelated recent topic {i}", "2026-10-30"))
        found = app.retrieve_relevant_conversation_turns("What did we discuss about my ESP32 robot car?", limit=3)
        self.assertEqual(len(found), 1)
        self.assertIn("ESP32", found[0]["user"])
        self.assertIn("driver", found[0]["assistant"])

    def test_does_not_return_unrelated_history(self):
        with app.db_connect() as conn:
            conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)", ("user", "I like learning Python programming.", "2026-10-30"))
            for i in range(14):
                conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)", ("user", f"Recent unrelated message {i}", "2026-10-30"))
        self.assertEqual(app.retrieve_relevant_conversation_turns("Tell me about my gardening plans", limit=3), [])

    def test_recall_is_bounded(self):
        with app.db_connect() as conn:
            for i in range(20):
                conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)", ("user", f"My ESP32 robot car project detail {i}", "2026-10-30"))
                conn.execute("INSERT INTO conversations(role,content,created) VALUES(?,?,?)", ("assistant", f"ESP32 robot car answer {i}", "2026-10-30"))
        self.assertLessEqual(len(app.retrieve_relevant_conversation_turns("Tell me about ESP32 robot car", limit=99)), 5)

if __name__ == "__main__":
    unittest.main()
