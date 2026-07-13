from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "implementations" / "claude-code" / "arf-academic"


def main() -> int:
    claude = shutil.which("claude")
    if claude is None:
        print("SKIP: Claude CLI not found; structural plugin tests remain authoritative.")
        return 0

    command = [claude, "plugin", "validate", str(PLUGIN_DIR)]
    result = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
