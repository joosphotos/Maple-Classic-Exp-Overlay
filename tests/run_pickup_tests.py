"""Runs every pickup log test (tests/test_pickup_*.py), one after another, each in its own Python.

Each pickup ticket (docs/pickup-log/TICKETS.md) adds its own test_pickup_<part>.py, so tickets built at the same
time never edit the same test file or the CI workflow. Tests that need the private recordings read them from the
folder in MAPLE_CAPTURES and say "skipped" when it isn't set (as on GitHub's CI); everything else always runs.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    tests = sorted(HERE.glob("test_pickup_*.py"))
    if not tests:
        print("No pickup log tests yet.")
        return 0
    failed = []
    for t in tests:
        print(f"== {t.name}", flush=True)
        if subprocess.run([sys.executable, str(t)]).returncode:
            failed.append(t.name)
    print(f"{len(tests) - len(failed)} of {len(tests)} pickup test files passed" + (f"; failed: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
