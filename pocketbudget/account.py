class Account:
    def __init__(self) -> None:
        self._balance = 0
        self._history: list[tuple[str, int]] = []

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

    def add_expense(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("expense amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient balance")
        self._balance -= amount
        self._history.append(("expense", amount))
