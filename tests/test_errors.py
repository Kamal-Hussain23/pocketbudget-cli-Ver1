from pathlib import Path

import pytest

from pocketbudget import storage
from pocketbudget.account import Account
from pocketbudget.exceptions import (
    BudgetExceededError,
    CorruptedDataError,
    InsufficientBalanceError,
    InvalidAmountError,
    InvalidBudgetError,
    InvalidCategoryError,
)


def test_negative_income_raises_invalid_amount() -> None:
    account = Account()
    with pytest.raises(InvalidAmountError):
        account.add_income(-100)
    assert account.balance == 0
    assert account.history == []


def test_negative_expense_raises_invalid_amount() -> None:
    account = Account()
    account.add_income(100)
    with pytest.raises(InvalidAmountError):
        account.add_expense(-50)
    assert account.balance == 100
    assert account.history == [("income", 100)]


def test_zero_amount_raises_invalid_amount() -> None:
    account = Account()
    with pytest.raises(InvalidAmountError):
        account.add_income(0)
    with pytest.raises(InvalidAmountError):
        account.add_expense(0)


def test_invalid_category_raises_invalid_category() -> None:
    account = Account()
    account.add_income(100)
    with pytest.raises(InvalidCategoryError):
        account.add_expense(10, "Clothing")
    with pytest.raises(InvalidCategoryError):
        account.set_budget("Clothing", 100)


def test_invalid_budget_limit_raises_invalid_budget() -> None:
    account = Account()
    with pytest.raises(InvalidBudgetError):
        account.set_budget("Food", 0)


def test_expense_over_budget_raises_budget_exceeded() -> None:
    account = Account()
    account.add_income(100)
    account.set_budget("Food", 50)
    with pytest.raises(BudgetExceededError):
        account.add_expense(80, "Food")
    assert account.balance == 100
    assert account.history == [("income", 100)]
    assert account.remaining_budget("Food") == 50


def test_expense_over_balance_raises_insufficient_balance() -> None:
    account = Account()
    account.add_income(100)
    with pytest.raises(InsufficientBalanceError):
        account.add_expense(150)
    assert account.balance == 100


def test_corrupted_json_raises_corrupted_data(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text("{this is not valid json")
    with pytest.raises(CorruptedDataError):
        storage.load(path)


def test_corrupted_non_dict_raises_corrupted_data(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text("[1, 2, 3]")
    with pytest.raises(CorruptedDataError):
        storage.load(path)


def test_corrupted_negative_balance_raises_corrupted_data(tmp_path: Path) -> None:
    path = tmp_path / "budget.json"
    path.write_text('{"balance": -5, "history": []}')
    with pytest.raises(CorruptedDataError):
        storage.load(path)
