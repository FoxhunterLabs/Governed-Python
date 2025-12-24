# Governed Python

Governed Python is a restricted authoring profile for writing
**protocol logic and autonomy-critical code** in Python.

It is a **static checker**, not a runtime, sandbox, or security system.

---

## The Problem

Python is excellent for expressing logic, but it is difficult to:
- restrict authority (time, randomness, I/O) in a reviewable way
- reason about protocol state transitions
- prevent accidental secret leakage
- enforce determinism at the authoring level
- review code for correctness rather than intent

Governed Python addresses these issues by **removing degrees of freedom**.

---

## What Governed Python Enforces

- **Explicit authority**
  - Time, randomness, I/O, storage, and audit access require capabilities.
- **Linear capabilities**
  - Capabilities are move-only and cannot be duplicated or returned.
- **Secret hygiene**
  - Secrets cannot be stringified, logged, or passed to output sinks.
- **Protocol correctness**
  - State machines are explicit and transitions are checked.
- **Deterministic authoring**
  - No unbounded loops or implicit nondeterminism.

All rules are defined in `SPEC.md` and enforced statically.

---

## What Governed Python Does *Not* Do

- It does **not** sandbox execution.
- It does **not** make runtime security guarantees.
- It does **not** replace Python.
- It does **not** prevent malicious code.

Governed Python is about **correctness and reviewability**, not defense-in-depth.

---

## Example: Failing Code

```python
def f(key: Secret[int]) -> int:
    print(key)   # ❌ secret sink
    return 0
ERROR [SE4]: Secret passed to sink 'print'
________________________________________
Guarantees
If code passes the checker:
•	All protocol transitions are explicit and valid.
•	Secrets are not trivially leaked via strings or logs.
•	Nondeterminism is surfaced via explicit parameters.
•	Reviewers can reason locally about authority and state.
________________________________________
Non-Guarantees
•	Secrets are not protected at runtime.
•	Capabilities do not enforce isolation by themselves.
•	Passing the checker does not imply safety or security.
________________________________________
Status
This project is experimental and intentionally conservative.
The goal is to explore a correctness-oriented Python authoring subset
and understand its tradeoffs.
Feedback from language and tooling practitioners is welcome.
