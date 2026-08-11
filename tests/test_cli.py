import subprocess
import sys
from pathlib import Path

from pocketbudget import storage


def run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pocketbudget", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_add_income_records_deposit(tmp_path: Path) -> None:
    result = run_cli("add-income", "100", "Food", cwd=tmp_path)
    assert result.returncode == 0
    assert "Income recorded" in result.stdout


def test_add_expense_records_expense(tmp_path: Path) -> None:
    run_cli("add-income", "100", "Food", cwd=tmp_path)
    result = run_cli("add-expense", "30", "Food", cwd=tmp_path)
    assert result.returncode == 0
    assert "Expense recorded" in result.stdout


def test_show_balance_prints_current_balance(tmp_path: Path) -> None:
    run_cli("add-income", "100", "Food", cwd=tmp_path)
    result = run_cli("show-balance", cwd=tmp_path)
    assert result.returncode == 0
    assert "Balance: $100" in result.stdout


def test_show_history_displays_all_transactions(tmp_path: Path) -> None:
    run_cli("add-income", "100", "Food", cwd=tmp_path)
    run_cli("add-expense", "30", "Food", cwd=tmp_path)
    result = run_cli("show-history", cwd=tmp_path)
    assert result.returncode == 0
    assert "income" in result.stdout
    assert "100" in result.stdout
    assert "expense" in result.stdout
    assert "30" in result.stdout


def test_set_budget_sets_category_limit(tmp_path: Path) -> None:
    result = run_cli("set-budget", "Food", "100", cwd=tmp_path)
    assert result.returncode == 0
    assert "Budget set" in result.stdout


def test_show_summary_displays_spending_against_budget(tmp_path: Path) -> None:
    run_cli("set-budget", "Food", "100", cwd=tmp_path)
    run_cli("add-income", "200", "Food", cwd=tmp_path)
    run_cli("add-expense", "40", "Food", cwd=tmp_path)
    result = run_cli("show-summary", cwd=tmp_path)
    assert result.returncode == 0
    assert "Food: $40 / $100" in result.stdout
    assert "Utilities: $0 / no budget" in result.stdout
    assert "Entertainment: $0 / no budget" in result.stdout
    assert "Transport: $0 / no budget" in result.stdout


def test_expense_over_budget_is_blocked(tmp_path: Path) -> None:
    run_cli("set-budget", "Food", "50", cwd=tmp_path)
    run_cli("add-income", "100", "Food", cwd=tmp_path)
    result = run_cli("add-expense", "80", "Food", cwd=tmp_path)
    assert result.returncode != 0
    assert "budget" in result.stderr
    balance = run_cli("show-balance", cwd=tmp_path)
    assert "Balance: $100" in balance.stdout


def test_expense_with_invalid_category_is_rejected(tmp_path: Path) -> None:
    run_cli("add-income", "100", "Food", cwd=tmp_path)
    result = run_cli("add-expense", "10", "Clothing", cwd=tmp_path)
    assert result.returncode != 0
    assert "category" in result.stderr


def test_state_persists_across_invocations(tmp_path: Path) -> None:
    run_cli("add-income", "50", "Food", cwd=tmp_path)
    run_cli("add-income", "30", "Food", cwd=tmp_path)
    balance = run_cli("show-balance", cwd=tmp_path)
    assert balance.returncode == 0
    assert "Balance: $80" in balance.stdout
    assert (tmp_path / storage.DEFAULT_DATA_FILE).exists()
