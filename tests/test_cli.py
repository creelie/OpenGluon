import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EntryPointTests(unittest.TestCase):
    def test_module_and_compatible_entry_points(self):
        for command in (["anaxia.py"], ["opengluon.py"], ["-m", "anaxia"]):
            result = subprocess.run([sys.executable, *command, "--help"], cwd=ROOT,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("radar", result.stdout)
            self.assertIn("certify", result.stdout)


if __name__ == "__main__":
    unittest.main()
