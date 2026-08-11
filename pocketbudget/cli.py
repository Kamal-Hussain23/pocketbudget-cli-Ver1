import sys
from collections.abc import Callable
from typing import NoReturn

from pocketbudget import storage
from pocketbudget.account import VALID_CATEGORIES

Command = Callable[[list[str]], None]


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print("Hello PocketBudget")
        return
    _run_command(args)


def _run_command(args: list[str]) -> None:
    commands: dict[str, Command] = {
        "add-income": _add_income,
        "add-expense": _add_expense,
        "show-balance": _show_balance,
        "show-history": _show_history,
        "set-budget": _set_budget,
        "show-summary": _show_summary,
    }
    handler = commands.get(args[0])
    if handler is None:
        _fail(f"unknown command: {args[0]}")
    handler(args[1:])


def _add_income(args: list[str]) -> None:
    amount = int(args[0])
    category = args[1]
    _validate_category(category)
    account = storage.load()
    account.add_income(amount)
    storage.save(account)
    print(f"Income recorded: ${amount} in {category}")


def _add_expense(args: list[str]) -> None:
    amount = int(args[0])
    category = args[1]
    account = storage.load()
    try:
        account.add_expense(amount, category)
    except ValueError as error:
        _fail(str(error))
    storage.save(account)
    print(f"Expense recorded: ${amount} in {category}")


def _show_balance(_args: list[str]) -> None:
    account = storage.load()
    print(f"Balance: ${account.balance}")


def _show_history(_args: list[str]) -> None:
    account = storage.load()
    for entry in account.history:
        print(" ".join(str(item) for item in entry))


def _set_budget(args: list[str]) -> None:
    category = args[0]
    limit = int(args[1])
    account = storage.load()
    try:
        account.set_budget(category, limit)
    except ValueError as error:
        _fail(str(error))
    storage.save(account)
    print(f"Budget set: {category} ${limit}")


def _show_summary(_args: list[str]) -> None:
    account = storage.load()
    for category, budget in account.budgets.items():
        remaining = account.remaining_budget(category)
        spent = budget - remaining if remaining is not None else budget
        print(f"{category}: ${spent} / ${budget}")


def _validate_category(category: str) -> None:
    if category not in VALID_CATEGORIES:
        _fail(f"invalid category: {category}")


def _fail(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
