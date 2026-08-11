# pocketbudget-cli-Ver1

A personal expense and budget tracking CLI. Track income and expenses against
per-category budgets, with state persisted to `data/budget.json`.

## Commands

- `add-income <amount> <category>` — records a deposit.
- `add-expense <amount> <category>` — records an expense, validated against
  category budgets and the total balance.
- `show-balance` — prints the current balance.
- `show-history` — lists all executed transactions.
- `set-budget <category> <limit>` — sets a spending ceiling for a category.
- `show-summary` — shows category-by-category spending against budgets.

Every command follows the same lifecycle: load the saved state, run the domain
operation, save the result.

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

The application state is encapsulated behind private attributes, exposed
read-only through properties (with defensive copies), and every mutation flows
through validated domain methods — so the balance and transaction list can
never be changed by direct assignment, only by intentional, validated
operations.
