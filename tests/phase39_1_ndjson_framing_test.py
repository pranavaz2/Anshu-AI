\
import json
import unittest

def encode_events(reply):
    return (
        (json.dumps({"type":"delta","text":reply}, ensure_ascii=False)+"\n").encode("utf-8")
        + (json.dumps({"type":"done","result":{"reply":reply,"action":"none"},"model":"local"}, ensure_ascii=False)+"\n").encode("utf-8")
    )

class Phase391NdjsonFramingTests(unittest.TestCase):
    def test_events_are_separated_by_real_newlines(self):
        payload = encode_events("Obstacle avoidance status.")
        self.assertEqual(payload.count(b"\n"), 2)
        self.assertNotIn(b"\\\\n", payload)
        lines = payload.decode("utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["type"], "delta")
        self.assertEqual(json.loads(lines[1])["type"], "done")

if __name__ == "__main__":
    unittest.main()
