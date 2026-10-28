"""Offline oracle for the persistence fixture; no agent or grader calls.

Run: python3 scripts/test-driven-development-fixture-test.py
The reference control uses the same SQLite write boundary in a transaction.
It checks fixture sensitivity, not whether an agent follows the TDD workflow.
"""

from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest


FIXTURE = Path(__file__).resolve().parents[1] / "evals" / "fixtures" / "test-driven-development-persistence"
sys.path.insert(0, str(FIXTURE))
from vault import initialize, snapshot


class PersistenceFixtureTest(unittest.TestCase):
    def test_existing_success_and_exception_tests_pass(self):
        result = subprocess.run(
            [sys.executable, "-m", "unittest",
             "test_vault.ReplaceSecretTest.test_success_persists_replacement_and_audit",
             "test_vault.ReplaceSecretTest.test_exception_restores_previous_value"],
            cwd=FIXTURE,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def terminate_at_write_boundary(self, source):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "vault.sqlite"
            initialize(database)
            result = subprocess.run(
                [sys.executable, "-B", "-c", source, str(database)],
                cwd=FIXTURE, capture_output=True, text=True, timeout=10,
            )
            self.assertEqual(result.returncode, 23, result.stderr)
            return snapshot(database)

    def test_legacy_compensation_leaves_unaudited_replacement(self):
        observed = self.terminate_at_write_boundary("""
import os, sys
from vault import replace_secret
replace_secret(sys.argv[1], 'new', lambda: os._exit(23))
""")
        self.assertEqual(observed, ("new", []))

    def test_transaction_control_rolls_back_after_same_termination(self):
        observed = self.terminate_at_write_boundary("""
import os, sqlite3, sys
with sqlite3.connect(sys.argv[1]) as connection:
    connection.execute("UPDATE secret SET value = 'new'")
    os._exit(23)
    connection.execute("INSERT INTO audit VALUES ('new')")
""")
        self.assertEqual(observed, ("old", []))


if __name__ == "__main__":
    unittest.main()
