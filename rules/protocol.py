# governed/rules/protocol.py
from __future__ import annotations

import ast
from typing import Dict, List, Set, Tuple

from governed.ast.context import Context
from governed.diagnostics import Diagnostic, Severity


def check(tree: ast.AST, ctx: Context) -> List[Diagnostic]:
    diagnostics: List[Diagnostic] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        # P1 — protocol declaration
        if not _has_decorator(node, "protocol"):
            continue

        protocol_name = node.name
        states: Set[str] = set()
        transitions: List[Tuple[str, str, ast.FunctionDef]] = []

        # Collect states and transitions
        for item in node.body:

            # P2 — state declaration
            if isinstance(item, ast.ClassDef) and _has_decorator(item, "state"):
                states.add(item.name)

            # P4 — transition declaration
            if isinstance(item, ast.FunctionDef):
                for dec in item.decorator_list:
                    if isinstance(dec, ast.Call) and _decorator_name(dec) == "transition":
                        from_state, to_state = _parse_transition(dec)
                        transitions.append((from_state, to_state, item))

        # P3 — initial state
        if not states:
            diagnostics.append(
                Diagnostic(
                    severity=Severity.ERROR,
                    message=f"Protocol '{protocol_name}' declares no states",
                    rule_id="P3",
                    line=node.lineno,
                    column=node.col_offset,
                )
            )

        # P7 — validate state references
        for from_state, to_state, fn in transitions:
            if from_state not in states:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Transition '{fn.name}' references unknown state '{from_state}'",
                        rule_id="P7",
                        line=fn.lineno,
                        column=fn.col_offset,
                    )
                )
            if to_state not in states:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Transition '{fn.name}' references unknown state '{to_state}'",
                        rule_id="P7",
                        line=fn.lineno,
                        column=fn.col_offset,
                    )
                )

            # P5 — transition return type must be Result
            if fn.returns is None or not _is_result_annotation(fn.returns):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message=f"Transition '{fn.name}' must return Result[Ok[State], Err[E]]",
                        rule_id="P5",
                        line=fn.lineno,
                        column=fn.col_offset,
                    )
                )

        # P8 — reachability (warning only)
        reachable = _compute_reachable(states, transitions)
        unreachable = states - reachable
        if unreachable:
            diagnostics.append(
                Diagnostic(
                    severity=Severity.WARNING,
                    message=f"Unreachable states in protocol '{protocol_name}': {', '.join(sorted(unreachable))}",
                    rule_id="P8",
                    line=node.lineno,
                    column=node.col_offset,
                )
            )

    return diagnostics


# ----------------- helpers -----------------


def _has_decorator(node: ast.AST, name: str) -> bool:
    return any(_decorator_name(d) == name for d in getattr(node, "decorator_list", []))


def _decorator_name(dec: ast.AST) -> str | None:
    if isinstance(dec, ast.Name):
        return dec.id
    if isinstance(dec, ast.Call):
        return _decorator_name(dec.func)
    return None


def _parse_transition(dec: ast.Call) -> Tuple[str, str]:
    from_state = None
    to_state = None

    for kw in dec.keywords:
        if kw.arg == "from_" and isinstance(kw.value, ast.Name):
            from_state = kw.value.id
        if kw.arg == "to" and isinstance(kw.value, ast.Name):
            to_state = kw.value.id

    return from_state or "", to_state or ""


def _is_result_annotation(node: ast.AST) -> bool:
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        return node.value.id == "Result"
    return False


def _compute_reachable(
    states: Set[str],
    transitions: List[Tuple[str, str, ast.FunctionDef]],
) -> Set[str]:
    if not states:
        return set()

    # First declared state is initial by convention
    initial = next(iter(states))
    reachable = {initial}

    changed = True
    while changed:
        changed = False
        for src, dst, _ in transitions:
            if src in reachable and dst not in reachable:
                reachable.add(dst)
                changed = True

    return reachable
