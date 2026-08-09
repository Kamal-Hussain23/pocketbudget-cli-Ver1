import subprocess
import sys


def test_entry_point_console_script() -> None:
    result = subprocess.run(["pocketbudget"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Hello PocketBudget" in result.stdout


def test_entry_point_python_m() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pocketbudget"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Hello PocketBudget" in result.stdout
