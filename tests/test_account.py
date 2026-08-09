import pytest

from pocketbudget.account import Account


def test_balance_readable_from_outside() -> None:
    account = Account()
    assert account.balance == 0


def test_balance_cannot_be_assigned_from_outside() -> None:
    account = Account()
    with pytest.raises(AttributeError):
        setattr(account, "balance", 500)
    assert account.balance == 0


def test_add_income_increases_balance() -> None:
    account = Account()
    account.add_income(100)
    assert account.balance == 100


def test_add_expense_decreases_balance() -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(40)
    assert account.balance == 60


def test_balance_only_changes_through_methods() -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(30)
    assert account.balance == 70


def test_negative_income_is_invalid() -> None:
    account = Account()
    with pytest.raises(ValueError, match="positive"):
        account.add_income(-100)
    assert account.balance == 0


def test_negative_expense_is_invalid() -> None:
    account = Account()
    account.add_income(100)
    with pytest.raises(ValueError, match="positive"):
        account.add_expense(-50)
    assert account.balance == 100


def test_overdrawing_is_blocked() -> None:
    account = Account()
    account.add_income(100)
    with pytest.raises(ValueError, match="balance"):
        account.add_expense(150)
    assert account.balance == 100
