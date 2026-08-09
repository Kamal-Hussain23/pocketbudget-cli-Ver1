class Account:
    def __init__(self) -> None:
        self._balance = 0

    @property
    def balance(self) -> int:
        return self._balance

    def add_income(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("income amount must be positive")
        self._balance += amount

    def add_expense(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("expense amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient balance")
        self._balance -= amount
