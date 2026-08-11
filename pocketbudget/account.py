VALID_CATEGORIES = ("Food", "Utilities", "Entertainment", "Transport")


class Account:
    def __init__(self) -> None:
        self._balance = 0
        self._history: list[tuple[str, int]] = []
        self._budgets: dict[str, int] = {}
        self._spent: dict[str, int] = {}

    @property
    def balance(self) -> int:
        return self._balance

    @property
    def history(self) -> list[tuple[str, int]]:
        return self._history.copy()

    def add_income(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("income amount must be positive")
        self._balance += amount
        self._history.append(("income", amount))

    def add_expense(self, amount: int, category: str = "") -> None:
        if amount <= 0:
            raise ValueError("expense amount must be positive")
        if category and category not in VALID_CATEGORIES:
            raise ValueError("invalid category")
        if category in self._budgets and amount > self._remaining(category):
            raise ValueError("expense exceeds category budget")
        if amount > self._balance:
            raise ValueError("insufficient balance")
        self._balance -= amount
        self._history.append(("expense", amount))
        if category:
            self._spent[category] = self._spent.get(category, 0) + amount

    def set_budget(self, category: str, limit: int) -> None:
        if category not in VALID_CATEGORIES:
            raise ValueError("invalid category")
        if limit <= 0:
            raise ValueError("budget must be positive")
        self._budgets[category] = limit
        self._spent.setdefault(category, 0)

    def remaining_budget(self, category: str) -> int | None:
        if category not in self._budgets:
            return None
        return self._remaining(category)

    def _remaining(self, category: str) -> int:
        return self._budgets[category] - self._spent.get(category, 0)
