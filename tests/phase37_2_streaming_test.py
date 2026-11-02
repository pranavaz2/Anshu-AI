"""Regression test for NDJSON framing in direct saved-memory responses."""
from pathlib import Path
import unittest

SERVER = Path(__file__).resolve().parents[1] / "server.py"

class StreamingFramingTests(unittest.TestCase):
    def test_direct_memory_stream_uses_real_newline_delimiters(self):
        source = SERVER.read_text(encoding="utf-8")
        block_start = source.index('if bool(body.get("stream", False)):', source.index("direct_memory_reply"))
        block_end = source.index("                else:", block_start)
        block = source[block_start:block_end]
        self.assertIn('+"\\n").encode("utf-8"))', block)
        self.assertNotIn('+"\\\\n").encode("utf-8"))', block)

    def test_two_ndjson_events_can_be_split_and_parsed(self):
        import json
        events = [
            {"type": "delta", "text": "Your saved memory says Java."},
            {"type": "done", "result": {"reply": "Your saved memory says Java.", "action": "none"}, "model": "test"}
        ]
        wire = "".join(json.dumps(event) + "\n" for event in events)
        parsed = [json.loads(line) for line in wire.splitlines() if line.strip()]
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["text"], "Your saved memory says Java.")
        self.assertEqual(parsed[1]["result"]["reply"], "Your saved memory says Java.")

if __name__ == "__main__":
    unittest.main()
