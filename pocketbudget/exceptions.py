class InvalidAmountError(ValueError):
    """Raised when a transaction amount is not positive."""


class InvalidCategoryError(ValueError):
    """Raised when a category is not in the allowed list."""


class BudgetExceededError(ValueError):
    """Raised when an expense exceeds a category's remaining budget."""


class InsufficientBalanceError(ValueError):
    """Raised when an expense exceeds the total balance."""


class InvalidBudgetError(ValueError):
    """Raised when a budget limit is not positive."""


class CorruptedDataError(ValueError):
    """Raised when a saved data file is corrupted or invalid."""
