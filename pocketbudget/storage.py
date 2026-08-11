import json
from pathlib import Path
from typing import Any

from pocketbudget.account import Account
from pocketbudget.exceptions import CorruptedDataError

DEFAULT_DATA_FILE = Path("data") / "budget.json"


def save(account: Account, path: Path | None = None) -> None:
    target = path or DEFAULT_DATA_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {
        "balance": account.balance,
        "history": [list(entry) for entry in account.history],
    }
    if account.budgets:
        data["budgets"] = account.budgets
    target.write_text(json.dumps(data))


def load(path: Path | None = None) -> Account:
    source = path or DEFAULT_DATA_FILE
    if not source.exists():
        return Account()
    data = _read_data(source)
    _validate_balance(data)
    account = _rebuild_account(data["history"])
    _apply_budgets(account, data)
    if account.balance != data["balance"]:
        raise CorruptedDataError("balance does not match history")
    return account


def _read_data(source: Path) -> dict[str, Any]:
    try:
        data = json.loads(source.read_text())
    except json.JSONDecodeError as error:
        raise CorruptedDataError("corrupted budget file") from error
    if not isinstance(data, dict):
        raise CorruptedDataError("corrupted budget file")
    return data


def _validate_balance(data: dict[str, Any]) -> None:
    if not isinstance(data.get("balance"), int) or data["balance"] < 0:
        raise CorruptedDataError("invalid balance in budget file")
    if not isinstance(data.get("history"), list):
        raise CorruptedDataError("invalid history in budget file")


def _rebuild_account(history: Any) -> Account:
    account = Account()
    for entry in history:
        _apply_entry(account, entry)
    return account


def _apply_entry(account: Account, entry: Any) -> None:
    if not isinstance(entry, list) or len(entry) not in (2, 3):
        raise CorruptedDataError("invalid history entry in budget file")
    kind = entry[0]
    amount = entry[1]
    if kind == "income":
        account.add_income(amount)
    elif kind == "expense":
        category = entry[2] if len(entry) == 3 else ""
        account.add_expense(amount, category)
    else:
        raise CorruptedDataError("invalid history entry in budget file")


def _apply_budgets(account: Account, data: dict[str, Any]) -> None:
    budgets = data.get("budgets")
    if budgets is None:
        return
    if not isinstance(budgets, dict):
        raise CorruptedDataError("invalid budgets in budget file")
    for category, limit in budgets.items():
        if not isinstance(limit, int) or limit <= 0:
            raise CorruptedDataError("invalid budgets in budget file")
        account.set_budget(category, limit)
