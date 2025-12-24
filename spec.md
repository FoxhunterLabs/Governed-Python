````markdown
# Governed Python — Language Specification (SPEC.md)

This document defines the **authoring rules** for Governed Python.
All rules are extracted from the reference implementation and are **normative**.
Runtime behavior, sandboxing, tooling, and CLI concerns are explicitly out of scope.

---

## 1. Syntax Restrictions

**S1 — Forbidden Control Flow**  
The following syntax forms are forbidden:
- `while`
- `try / except / finally`
- `raise`
- `lambda`
- `async`, `await`
- `yield`, `yield from`
- `with`
- generator expressions
- list, set, and dict comprehensions

**S2 — Forbidden Mutable Literals**  
The following literals are forbidden in governed code:
- list literals (`[]`)
- dict literals (`{}`)
- set literals (`{a, b}`)

**S3 — Allowed Alternatives**  
- Tuples MAY be used.
- Immutable collections (`Vector`, `Map`) MAY be used where lists/dicts would otherwise appear.

**S4 — Match Exhaustiveness**  
Every `match` statement MUST include a wildcard (`case _`) arm.

**S5 — Abort on Wildcard**  
The wildcard arm of a `match` SHOULD call `abort(code)`.

**S6 — Import Restrictions**  
Only explicitly allowed imports MAY be used.
Relative imports are forbidden.

---

## 2. Capabilities

Capabilities represent authority-bearing resources and are **linear (move-only)**.

### Defined Capabilities
- `Clock`
- `Rng`
- `Io`
- `Store`
- `Audit`

**C1 — Capability Introduction**  
Capabilities MAY ONLY be introduced as function parameters.

**C2 — No Local Capabilities**  
Capabilities MUST NOT be created or assigned to local variables.

**C3 — No Capability Return**  
Functions MUST NOT return capabilities.

**C4 — Move Semantics**  
Passing a capability as an argument or assigning it to another name consumes it.
Consumed capabilities MUST NOT be used again.

**C5 — No Capability Mutation**  
Attributes or subscripts of capabilities MUST NOT be assigned.

**C6 — Method Whitelisting**  
Only explicitly allowed methods may be called on each capability type.

---

## 3. Secrets

Secrets represent sensitive data and are tracked explicitly.

**SE1 — Secret Type Form**  
Secrets are declared as `Secret[T]`, where `T` is an opaque label.
`T` has no runtime meaning and is used only for static distinction.

**SE2 — Secret Construction**  
Secrets MAY ONLY be produced by approved secret-returning operations.

**SE3 — No Secret to String**  
Secrets MUST NOT be:
- converted to strings
- interpolated into f-strings
- concatenated with strings

**SE4 — No Secret Sinks**  
Secrets MUST NOT be passed to output or logging functions.

**SE5 — Secret Assignment Safety**  
A non-secret value MUST NOT be assigned to a secret-typed variable.

**SE6 — Secret Consumption**  
Consumed secrets MUST NOT be reused.

---

## 4. Protocols and State Machines

Protocols define explicit state machines with verified transitions.

**P1 — Protocol Declaration**  
A protocol is a class decorated with `@protocol`.

**P2 — State Declaration**  
Protocol states are inner classes decorated with `@state`.

**P3 — Initial State**  
A protocol MUST define an initial state.
If none is explicitly named, the first declared state is the initial state.

**P4 — Transition Declaration**  
Transitions are functions decorated with:
```python
@transition(from_=StateA, to=StateB)
````

**P5 — Transition Signature**
Transition functions MUST:

* accept the source state as the first argument
* return `Result[Ok[State], Err[Error]]`

**P6 — No Implicit Transitions**
State changes MUST occur only via declared transitions.

**P7 — Valid State References**
All transitions MUST reference valid states declared in the protocol.

**P8 — Reachability**
Unreachable states are permitted but SHOULD be reported.

---

## 5. Result Types

**R1 — Result Usage**
Error handling MUST be expressed via `Result`, not exceptions.

**R2 — Transition Results**
All transitions MUST return a `Result` whose `Ok` variant contains the destination state.

---

## 6. Determinism (Authoring-Level)

**D1 — No Unbounded Loops**
Unbounded or condition-based looping constructs are forbidden.

**D2 — Explicit Authority for Nondeterminism**
Access to time or randomness MUST occur only via capabilities.

---

## Non-Goals

* Runtime security guarantees
* Sandboxing or execution isolation
* Performance characteristics
* IDE or tooling behavior

These concerns are explicitly outside the scope of this specification.

```
```
