import subprocess
import sys


def test_cli_help():
    r = subprocess.run(
        [sys.executable, "-m", "itb.cli", "--help"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "check" in r.stdout
    assert "serve" in r.stdout


def test_cli_check_pure_gr():
    r = subprocess.run(
        [sys.executable, "-m", "itb.cli", "check",
         "--g4", "0", "--g6", "0"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "feasible" in r.stdout.lower()


def test_cli_check_violation_exit_code():
    r = subprocess.run(
        [sys.executable, "-m", "itb.cli", "check",
         "--g4", "-1", "--g6", "0.5"],
        capture_output=True, text=True,
    )
    assert r.returncode == 2
