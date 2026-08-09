from pocketbudget.account import Account


def test_mutating_returned_history_does_not_change_account() -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(40)

    before = account.history.copy()
    history = account.history
    history.append(("mutated", 0))

    assert account.history == before


def test_clearing_returned_history_does_not_change_account() -> None:
    account = Account()
    account.add_income(100)
    account.add_expense(40)

    before = account.history.copy()
    history = account.history
    history.clear()

    assert account.history == before
