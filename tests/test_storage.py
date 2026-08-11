import json
from pathlib import Path

import pytest

from pocketbudget import storage
from pocketbudget.account import Account


def test_save_writes_account_state_to_default_data_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    account = Account()
    account.add_income(100)
    account.add_expense(40)
    storage.save(account)
    assert (tmp_path / "data" / "budget.json").exists()


def test_save_writes_balance_and_history(tmp_path: Path) -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(40)
    path = tmp_path / "budget.json"
    storage.save(account, path)
    assert json.loads(path.read_text()) == {
        "balance": 60,
        "history": [["income", 100], ["expense", 40]],
    }


def test_load_rebuilds_account_with_saved_state(tmp_path: Path) -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(40)
    path = tmp_path / "budget.json"
    storage.save(account, path)
    loaded = storage.load(path)
    assert loaded.balance == 60
    assert loaded.history == [("income", 100), ("expense", 40)]


def test_load_missing_file_returns_clean_account(tmp_path: Path) -> None:
    path = tmp_path / "missing.json"
    account = storage.load(path)
    assert account.balance == 0
    assert account.history == []


def test_load_corrupted_json_raises_error(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text("{this is not valid json")
    with pytest.raises(ValueError):
        storage.load(path)


def test_load_negative_balance_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text(json.dumps({"balance": -5, "history": []}))
    with pytest.raises(ValueError):
        storage.load(path)


def test_load_negative_history_amount_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text(json.dumps({"balance": 100, "history": [["income", -10]]}))
    with pytest.raises(ValueError):
        storage.load(path)


def test_load_overdrawn_history_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text(json.dumps({"balance": 100, "history": [["expense", 150]]}))
    with pytest.raises(ValueError):
        storage.load(path)


def test_load_inconsistent_balance_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text(json.dumps({"balance": 999, "history": [["income", 100]]}))
    with pytest.raises(ValueError):
        storage.load(path)
