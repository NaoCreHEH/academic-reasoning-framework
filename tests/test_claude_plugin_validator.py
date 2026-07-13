import subprocess
import unittest
from unittest.mock import patch

import scripts.validate_claude_plugin as validator


class ClaudePluginValidatorTests(unittest.TestCase):
    def test_missing_claude_cli_returns_success_with_skip(self) -> None:
        with patch("scripts.validate_claude_plugin.shutil.which", return_value=None):
            with patch("builtins.print") as printed:
                self.assertEqual(validator.main(), 0)
        self.assertIn("SKIP", printed.call_args[0][0])

    def test_installed_cli_invokes_expected_argument_list(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["claude"],
            returncode=0,
            stdout="ok",
            stderr="",
        )
        with patch(
            "scripts.validate_claude_plugin.shutil.which",
            return_value="C:/bin/claude",
        ):
            with patch(
                "scripts.validate_claude_plugin.subprocess.run",
                return_value=completed,
            ) as run:
                self.assertEqual(validator.main(), 0)
        args, kwargs = run.call_args
        self.assertEqual(args[0][0:3], ["C:/bin/claude", "plugin", "validate"])
        self.assertEqual(args[0][3], str(validator.PLUGIN_DIR))
        self.assertFalse(kwargs["check"])

    def test_validator_failure_returns_nonzero(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["claude"],
            returncode=7,
            stdout="",
            stderr="failed",
        )
        with patch(
            "scripts.validate_claude_plugin.shutil.which",
            return_value="claude",
        ):
            with patch(
                "scripts.validate_claude_plugin.subprocess.run",
                return_value=completed,
            ):
                self.assertEqual(validator.main(), 7)

    def test_shell_is_not_used(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["claude"],
            returncode=0,
            stdout="",
            stderr="",
        )
        with patch(
            "scripts.validate_claude_plugin.shutil.which",
            return_value="claude",
        ):
            with patch(
                "scripts.validate_claude_plugin.subprocess.run",
                return_value=completed,
            ) as run:
                validator.main()
        self.assertNotIn("shell", run.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
