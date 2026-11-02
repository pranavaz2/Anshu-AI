"""Small local HTTP security regression checks for ANSHU Phase 25."""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server as app  # noqa: E402


class SecuritySmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.httpd.daemon_threads = True
        cls.port = cls.httpd.server_port
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)

    def request(self, method, path, body=None, headers=None, host=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        base = {"Host": host or f"localhost:{self.port}"}
        if body is not None:
            base["Content-Type"] = "application/json"
        base.update(headers or {})
        conn.request(method, path, body=body, headers=base)
        response = conn.getresponse()
        data = response.read()
        status, response_headers = response.status, dict(response.getheaders())
        conn.close()
        return status, response_headers, data

    def test_ui_is_served(self):
        status, headers, data = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"ANSHU", data[:20000])
        self.assertEqual(headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")

    def test_head_does_not_expose_private_file_metadata(self):
        status, _headers, _data = self.request("HEAD", "/server.py")
        self.assertEqual(status, 404)

    def test_sensitive_files_are_not_served(self):
        for path in ("/server.py", "/README.txt", "/jarvis_local_data/jarvis_memory.db"):
            with self.subTest(path=path):
                status, _headers, _data = self.request("GET", path)
                self.assertEqual(status, 404)

    def test_non_loopback_host_rejected(self):
        status, _headers, _data = self.request("GET", "/", host="attacker.example")
        self.assertEqual(status, 403)

    def test_foreign_origin_rejected(self):
        status, _headers, _data = self.request(
            "POST", "/api/agent/plan", b'{"task":"open notepad"}',
            headers={"Origin": "http://attacker.example"})
        self.assertEqual(status, 403)

    def test_non_json_post_rejected(self):
        status, _headers, _data = self.request(
            "POST", "/api/agent/plan", b'task=open+notepad',
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        self.assertEqual(status, 415)

    def test_plan_parser_stays_allowlisted(self):
        plan, error = app.build_agent_plan("open Notepad")
        self.assertIsNone(error)
        self.assertEqual(plan, [{"type": "launch", "app": "notepad"}])
        plan, error = app.build_agent_plan("run powershell and delete files")
        self.assertIsNone(plan)
        self.assertTrue(error)

    def test_dangerous_file_extensions_blocked(self):
        self.assertTrue({".exe", ".bat", ".ps1", ".msi"}.issubset(app.BLOCKED_OPEN_EXTENSIONS))

    def test_offline_voice_rejects_invalid_language(self):
        status, _headers, data = self.request(
            "POST", "/api/voice/transcribe",
            json.dumps({"audio": "YQ==", "language": "xx"}).encode("utf-8"))
        self.assertEqual(status, 400)
        self.assertIn(b"English only", data)

    def test_offline_voice_requires_audio(self):
        status, _headers, data = self.request(
            "POST", "/api/voice/transcribe",
            json.dumps({"audio": "", "language": "en"}).encode("utf-8"))
        self.assertEqual(status, 400)
        self.assertIn(b"Audio is missing", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
