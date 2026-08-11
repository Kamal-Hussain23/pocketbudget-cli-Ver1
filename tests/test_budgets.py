import pytest

from pocketbudget.account import Account


def test_budget_can_be_set_for_a_category() -> None:
    account = Account()
    account.set_budget("Food", 100)
    assert account.remaining_budget("Food") == 100


def test_expense_reduces_remaining_budget() -> None:
    account = Account()
    account.add_income(500)
    account.set_budget("Food", 100)
    account.add_expense(30, "Food")
    assert account.remaining_budget("Food") == 70


def test_expense_within_budget_is_recorded() -> None:
    account = Account()
    account.add_income(500)
    account.set_budget("Food", 100)
    account.add_expense(40, "Food")
    assert account.balance == 460


def test_expense_over_category_budget_is_blocked() -> None:
    account = Account()
    account.add_income(500)
    account.set_budget("Food", 100)
    with pytest.raises(ValueError, match="budget"):
        account.add_expense(150, "Food")
    assert account.balance == 500
    assert account.remaining_budget("Food") == 100


def test_budget_exceeded_after_partial_spending_is_blocked() -> None:
    account = Account()
    account.add_income(500)
    account.set_budget("Food", 100)
    account.add_expense(80, "Food")
    with pytest.raises(ValueError, match="budget"):
        account.add_expense(50, "Food")
    assert account.balance == 420
    assert account.remaining_budget("Food") == 20


def test_budgets_are_per_category() -> None:
    account = Account()
    account.add_income(500)
    account.set_budget("Food", 100)
    account.set_budget("Transport", 50)
    account.add_expense(90, "Food")
    assert account.remaining_budget("Food") == 10
    assert account.remaining_budget("Transport") == 50


def test_expense_with_invalid_category_is_rejected() -> None:
    account = Account()
    account.add_income(500)
    with pytest.raises(ValueError, match="category"):
        account.add_expense(10, "Clothing")
    assert account.balance == 500


def test_setting_budget_for_invalid_category_is_rejected() -> None:
    account = Account()
    with pytest.raises(ValueError, match="category"):
        account.set_budget("Clothing", 100)
