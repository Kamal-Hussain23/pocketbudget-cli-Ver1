import json
from pathlib import Path
from typing import Any

from pocketbudget.account import Account

DEFAULT_DATA_FILE = Path("data") / "budget.json"


def save(account: Account, path: Path | None = None) -> None:
    target = path or DEFAULT_DATA_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "balance": account.balance,
        "history": [list(entry) for entry in account.history],
    }
    target.write_text(json.dumps(data))


def load(path: Path | None = None) -> Account:
    source = path or DEFAULT_DATA_FILE
    if not source.exists():
        return Account()
    data = _read_data(source)
    _validate_balance(data)
    account = _rebuild_account(data["history"])
    if account.balance != data["balance"]:
        raise ValueError("balance does not match history")
    return account


def _read_data(source: Path) -> dict[str, Any]:
    try:
        data = json.loads(source.read_text())
    except json.JSONDecodeError as error:
        raise ValueError("corrupted budget file") from error
    if not isinstance(data, dict):
        raise ValueError("corrupted budget file")
    return data


def _validate_balance(data: dict[str, Any]) -> None:
    if not isinstance(data.get("balance"), int) or data["balance"] < 0:
        raise ValueError("invalid balance in budget file")
    if not isinstance(data.get("history"), list):
        raise ValueError("invalid history in budget file")


def _rebuild_account(history: Any) -> Account:
    account = Account()
    for entry in history:
        _apply_entry(account, entry)
    return account


def _apply_entry(account: Account, entry: Any) -> None:
    if not isinstance(entry, list) or len(entry) != 2:
        raise ValueError("invalid history entry in budget file")
    kind, amount = entry
    if kind == "income":
        account.add_income(amount)
    elif kind == "expense":
        account.add_expense(amount)
    else:
        raise ValueError("invalid history entry in budget file")
