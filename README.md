# PocketBudget

A personal expense and budget tracking CLI. Track income and expenses against
per-category budgets from your terminal, with state persisted to
`data/budget.json`.

**The problem it solves:** keeping a budget in your head (or a spreadsheet) is
error-prone. PocketBudget gives you a single source of truth — a small,
fast, terminal-based tool that records every dollar in and out, enforces
per-category spending limits, and blocks overspending before it happens.

Rules come from `rules.md`: USD only, four valid categories (Food,
Utilities, Entertainment, Transport), expenses larger than the balance are
blocked, and expenses that exceed a category budget are blocked too.

## Installation & Setup

Requires **Python 3.11+**.

```bash
# 1. Clone the repository
git clone https://github.com/Kamal-Hussain23/pocketbudget-cli-Ver1.git
cd pocketbudget-cli-Ver1

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install the package (editable, includes the `pocketbudget` command)
pip install -e .

# 4. Install pre-commit hooks (ruff lint, ruff format, mypy strict, pytest)
pre-commit install
```

Verify the install:

```bash
pocketbudget
# Hello PocketBudget
```

## Usage Examples

Run every command from the project directory. State is saved to
`data/budget.json` after each command.

```bash
# Add income
pocketbudget add-income 200 Food
# Income recorded: $200 in Food

# Set a budget for a category
pocketbudget set-budget Food 100
# Budget set: Food $100

# Record an expense
pocketbudget add-expense 40 Food
# Expense recorded: $40 in Food

# An expense over the category budget is blocked
pocketbudget add-expense 80 Food
# Error: expense exceeds category budget

# An expense over the total balance is blocked
pocketbudget add-expense 500 Transport
# Error: insufficient balance

# View the current balance
pocketbudget show-balance
# Balance: $160

# List all transactions
pocketbudget show-history
# income 200
# expense 40 Food

# View category spending against budgets
pocketbudget show-summary
# Food: $40 / $100
# Utilities: $0 / no budget
# Entertainment: $0 / no budget
# Transport: $0 / no budget
```

## Running the Test Suite

All tests use `pytest` and assert behaviour against the public interface —
they also cover the encapsulation guarantees below.

```bash
# From the project root, with the venv activated
pytest -v
# 48 passed
```

The same suite runs automatically on every commit via the local `pytest`
pre-commit hook. Run all quality gates manually any time:

```bash
pre-commit run --all-files
```

## Design Decisions (Encapsulation Showcase)

### 1. State lives behind private attributes

In `pocketbudget/account.py`, the `Account` keeps all mutable state as
underscore-prefixed attributes:

```python
self._balance = 0
self._history = []
self._budgets = {}
self._spent = {}
```

There is no public `balance`, `history`, `budgets`, or `spent` attribute. The
underscore signals "internal — do not touch," and nothing outside the class is
allowed to read or write these fields directly.

### 2. Read access is exposed through read-only properties

Outsiders can *observe* state, but never *mutate* it:

```python
@property
def balance(self) -> int:
    return self._balance

@property
def history(self) -> list[...]:
    return self._history.copy()      # defensive copy
```

Two distinct protection mechanisms here:

- **`balance`** is a read-only property with no setter. `account.balance = 500`
  raises `AttributeError` — proven by `test_balance_cannot_be_assigned_from_outside`
  in `tests/test_account.py`. The only way money moves is through domain methods.
- **`history` and `budgets`** return a **copy** (`._copy()`) rather than the
  internal list/dict. This is the defensive-copy pattern: the caller gets a
  working snapshot, so even mutating what they received can't corrupt the
  account. Proven by `tests/test_history.py`, which appends/clears the returned
  list and asserts the account's own history is untouched.

### 3. All writes flow through domain methods

Every state change goes through an explicit, validated method — never direct
assignment:

- `add_income(amount)` — the only way money is added.
- `add_expense(amount, category)` — the only way money is spent.
- `set_budget(category, limit)` — the only way a budget is created.

Reads that need derived state go through accessor methods too, so outsiders
never reach inside:

- `spent_in(category)` — how much a category has been spent.
- `remaining_budget(category)` — the budget left for a category.

This is the "domain methods over direct property access" principle: the class
owns its invariants, so callers can't leave it in an illegal state.

### 4. Validation runs *before* any mutation

Every mutator is a guard-then-act sequence. All `raise` statements come before
the first write:

- `add_income` rejects `amount <= 0` before touching `_balance`/`_history`.
- `add_expense` validates amount → category → budget → balance, **all four
  checks before** `self._balance -= amount`.
- `set_budget` validates category and limit before writing `_budgets`.

`tests/test_errors.py` locks this in — e.g. `test_negative_expense_raises_invalid_amount`
asserts that after a failed call the balance and history are **unchanged**, and
`test_expense_over_budget_raises_budget_exceeded` verifies the remaining budget
is intact.

### 5. Persistence respects the same boundary

`storage.save`/`load` only talk to the public interface: they read via
`account.balance`, `account.history`, `account.budgets`, and rebuild via
`account.add_income` / `account.add_expense` / `account.set_budget`. This means
**even data coming back from disk passes through the same validation as live
data** — a corrupted file can't inject a negative balance or an overdrawn
history, because the load path reuses the guarded domain methods
(`tests/test_storage.py`, `tests/test_errors.py`).

### Summary

| State | Private storage | Public read | Direct write? |
|---|---|---|---|
| Balance | `_balance` | `balance` (property, no setter) | No — `add_income`/`add_expense` |
| Transactions | `_history` | `history` (copy) | No — `add_income`/`add_expense` |
| Budgets | `_budgets` | `budgets` (copy) | No — `set_budget` |
| Spending per category | `_spent` | `spent_in(category)` | No — `add_expense` |

The application state is encapsulated behind private attributes, exposed
read-only through properties (with defensive copies), and every mutation flows
through validated domain methods — so the balance and transaction list can
never be changed by direct assignment, only by intentional, validated
operations.
