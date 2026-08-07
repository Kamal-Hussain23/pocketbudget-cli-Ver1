# Application Domain Rules

This document is the source of truth for your TDD loop. Fill in each section **before** you write any code — every rule you write here becomes at least one test.

There are no wrong answers, but there are inconsistent ones. Once you decide a rule, your code has to match it.

---

## 1. Currency Symbol

*What currency does your application use, and how is money formatted when it's displayed?*

> $Only categories Food and Transport should be allowed

---

## 2. Standard Categories

*Which expense categories are allowed? Limit yourself to 3–5. What happens if someone uses a category that isn't on your list?*

> _Your answer:_

---

## 3. Overspending Behaviour (Total Balance)

*What happens when an expense is larger than the total balance? Does your app allow the balance to go negative, or does it block the transaction? If it blocks, what does the caller get back?*

>Block and give an error message

---

## 4. Budget Limits (Category Budgets)

*What happens when an expense exceeds a category's budget limit, but the balance could still cover it? Is it blocked, or is it recorded with a warning?*

> Transaction is blocked and error message is displayed

---

## TDD Blueprint

Now turn each rule above into the test you will write **before** the implementation exists. Name the behaviour you'd assert.

- [ ] Rule 1 (Currency) →only Dollar currency should be allowed any other currency should result in error message

- [ ] Rule 2 (Categories) →only  Only categories Food and Transport should be possible. Error message should be displayed in case of other category.
- [ ] Rule 3 (Overspending) →Display error message in case of overspending.
- [ ] Rule 4 (Budget Limits) →Block transaction and error message is displayed
