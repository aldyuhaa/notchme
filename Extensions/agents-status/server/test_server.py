import copy
import importlib.util
import pathlib
import tempfile
import time
import unittest
from unittest import mock


SERVER_PATH = pathlib.Path(__file__).with_name("server.py")
SPEC = importlib.util.spec_from_file_location("agents_status_server", SERVER_PATH)
server = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(server)


class AgentsStatusServerTests(unittest.TestCase):
    def setUp(self):
        self._sessions = copy.deepcopy(server._sessions)
        self._recently_ended = copy.deepcopy(server._recently_ended_pids)
        server._sessions.clear()
        server._recently_ended_pids.clear()

    def tearDown(self):
        server._sessions.clear()
        server._sessions.update(self._sessions)
        server._recently_ended_pids.clear()
        server._recently_ended_pids.update(self._recently_ended)

    def _session(self, **overrides):
        base = {
            "agent": "Claude",
            "session_id": "session-1",
            "state": "Idle",
            "title": "",
            "cwd": "/tmp",
            "terminal": "Warp",
            "pid": 99999,
            "turn_id": None,
            "turn_active": False,
            "turn_started_at": None,
            "last_event": "Stop",
            "last_assistant_message": None,
            "error_expires_at": None,
            "updated_at": 100.0,
            "synthetic": False,
            "transcript_path": "",
        }
        base.update(overrides)
        return base

    def test_ended_event_removes_claude_session_by_pid(self):
        server._sessions[("Claude", "real-session")] = self._session(
            session_id="real-session",
            pid=42424,
        )

        ok, payload = server._apply_event({
            "state": "Ended",
            "agent": "Claude",
            "session_id": "default",
            "pid": 42424,
        })

        self.assertTrue(ok)
        self.assertTrue(payload["removed"])
        self.assertNotIn(("Claude", "real-session"), server._sessions)
        self.assertTrue(server._pid_recently_ended(42424, time.time()))

    def test_idle_claude_exit_prunes_without_error(self):
        key = ("Claude", "session-1")
        server._sessions[key] = self._session(pid=51515, state="Idle", turn_active=False)

        with mock.patch.object(server, "_pid_alive", return_value=False):
            now = 200.0
            server._mark_unexpected_claude_exits(now)
            self.assertEqual(server._sessions[key]["state"], "Idle")
            server._prune(now, ttl=999.0)

        self.assertNotIn(key, server._sessions)

    def test_codex_interrupt_marker_flips_working_session_idle(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            handle.write(
                "<turn_aborted>\n"
                "  <turn_id>turn-123</turn_id>\n"
                "  <reason>interrupted</reason>\n"
                "</turn_aborted>\n"
            )
            transcript_path = handle.name

        key = ("Codex", "session-1")
        server._sessions[key] = self._session(
            agent="Codex",
            state="Working",
            pid=61616,
            turn_id="turn-123",
            turn_active=True,
            transcript_path=transcript_path,
        )

        try:
            server._decay_working(300.0)
        finally:
            pathlib.Path(transcript_path).unlink(missing_ok=True)

        self.assertEqual(server._sessions[key]["state"], "Idle")
        self.assertFalse(server._sessions[key]["turn_active"])
        self.assertIsNone(server._sessions[key]["turn_started_at"])


    def test_muse_interactive_process_detected(self):
        self.assertTrue(server._muse_is_interactive_process("muse", "muse"))
        self.assertTrue(server._muse_is_interactive_process("muse-bin-1.4.10", "muse-bin-1.4.10"))
        self.assertTrue(server._muse_is_interactive_process("bash", "/bin/bash /tmp/fakebin/muse"))
        self.assertFalse(server._muse_is_interactive_process("muse-bin-1.4.10", "muse-bin-1.4.10 serve"))
        self.assertFalse(server._muse_is_interactive_process("muse", "muse exec 'ls'"))
        self.assertFalse(server._muse_is_interactive_process("muse", "muse --help"))
        self.assertFalse(server._muse_is_interactive_process("node", "node /tmp/x.js"))

    def test_opencode_interactive_process_detected(self):
        self.assertTrue(server._opencode_is_interactive_process("opencode.exe", "opencode.exe"))
        self.assertTrue(server._opencode_is_interactive_process("opencode", "opencode serve"))
        self.assertFalse(server._opencode_is_interactive_process("opencode", "opencode run 'fix bug'"))
        self.assertFalse(server._opencode_is_interactive_process("opencode", "opencode --help"))
        self.assertFalse(server._opencode_is_interactive_process("node", "node server.js"))

    def test_codebuddy_interactive_process_detected(self):
        self.assertTrue(server._codebuddy_is_interactive_process("node", "node /Users/x/.local/bin/codebuddy"))
        self.assertTrue(server._codebuddy_is_interactive_process("codebuddy", "codebuddy"))
        self.assertFalse(server._codebuddy_is_interactive_process("node", "node /Users/x/.local/bin/codebuddy -p 'hi'"))
        self.assertFalse(server._codebuddy_is_interactive_process("node", "node other.js"))

    def test_proc_sync_adds_working_and_removes_dead(self):
        now = time.time()
        with mock.patch.object(server, "_pid_alive", return_value=True), \
             mock.patch.object(server, "_cwd_for_pid", return_value="/tmp"), \
             mock.patch.object(server, "_infer_terminal_from_pid", return_value=""):
            cands = [{
                "agent": "Muse", "session_id": "pid:111", "state": "Working",
                "title": "", "cwd": "/tmp", "terminal": "",
                "pid": 111, "synthetic": True,
            }]
            server._sync_proc_sessions(now, cands)
            self.assertEqual(server._sessions[("Muse", "pid:111")]["state"], "Working")

        with mock.patch.object(server, "_pid_alive", return_value=False):
            server._sync_proc_sessions(now + 5, [])
            self.assertNotIn(("Muse", "pid:111"), server._sessions)

    def test_codebuddy_install_uninstall_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "settings.json"
            with mock.patch.object(server, "CB_SETTINGS_PATH", path):
                events = server.cb_install()
                self.assertIn("UserPromptSubmit", events)
                self.assertIn("Stop", events)
                status = server.cb_status()
                self.assertTrue(status["installed"])
                # Idempotent-ish: purge-then-add keeps exactly one group per event.
                server.cb_install()
                d = server._load_json_settings(path)
                for bucket in d["hooks"].values():
                    self.assertEqual(len(bucket), 1)
                removed = server.cb_uninstall()
                self.assertIn("UserPromptSubmit", removed)
                self.assertFalse(server.cb_status()["installed"])

    def test_generic_agent_event_accepted(self):
        ok, payload = server._apply_event({
            "state": "Working",
            "agent": "Mausbot",
            "session_id": "bot-1",
            "cwd": "/tmp",
        })
        self.assertTrue(ok)
        self.assertEqual(server._sessions[("Mausbot", "bot-1")]["state"], "Working")


if __name__ == "__main__":
    unittest.main()
