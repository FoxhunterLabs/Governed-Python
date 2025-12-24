# governed/rules/capabilities.py
from __future__ import annotations

import ast
from typing import List, Set

from governed.ast.context import Context, Symbol
from governed.diagnostics import Diagnostic, Severity


CAPABILITY_TYPES: Set[str] = {"Clock", "Rng", "Io", "Store", "Audit"}


def check(tree: ast.AST, ctx: Context) -> List[Diagnostic]:
    diagnostics: List[Diagnostic] = []

    for node in ast.walk(tree):

        # C1 / C2 — capabilities may only appear as function parameters
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.annotation, ast.Name):
                if node.annotation.id in CAPABILITY_TYPES:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            message=f"Capability '{node.annotation.id}' may not be declared as a local variable",
                            rule_id="C2",
                            suggestion="Declare capabilities only as function parameters",
                            line=node.lineno,
                            column=node.col_offset,
                        )
                    )

        # Track function scopes and parameters
        if isinstance(node, ast.FunctionDef):
            ctx.push_scope(f"func:{node.name}")

            for arg in node.args.args:
                if isinstance(arg.annotation, ast.Name):
                    if arg.annotation.id in CAPABILITY_TYPES:
                        ctx.current_scope.define(
                            Symbol(
                                name=arg.arg,
                                kind="capability",
                                node=arg,
                            )
                        )

            # Walk function body manually to catch usage
            for inner in ast.walk(node):

                # C4 — move semantics (assignment consumes capability)
                if isinstance(inner, ast.Assign):
                    if isinstance(inner.value, ast.Name):
                        sym = ctx.current_scope.lookup(inner.value.id)
                        if sym and sym.kind == "capability":
                            sym.consumed = True

                # C4 — use after consume
                if isinstance(inner, ast.Name) and isinstance(inner.ctx, ast.Load):
                    sym = ctx.current_scope.lookup(inner.id)
                    if sym and sym.kind == "capability" and sym.consumed:
                        diagnostics.append(
                            Diagnostic(
                                severity=Severity.ERROR,
                                message=f"Use of consumed capability '{inner.id}'",
                                rule_id="C4",
                                line=inner.lineno,
                                column=inner.col_offset,
                            )
                        )

                # C3 — returning capabilities
                if isinstance(inner, ast.Return):
                    if isinstance(inner.value, ast.Name):
                        sym = ctx.current_scope.lookup(inner.value.id)
                        if sym and sym.kind == "capability":
                            diagnostics.append(
                                Diagnostic(
                                    severity=Severity.ERROR,
                                    message=f"Capabilities must not be returned from functions",
                                    rule_id="C3",
                                    line=inner.lineno,
                                    column=inner.col_offset,
                                )
                            )

                # C5 — capability mutation
                if isinstance(inner, ast.Attribute):
                    if isinstance(inner.value, ast.Name):
                        sym = ctx.current_scope.lookup(inner.value.id)
                        if sym and sym.kind == "capability":
                            if isinstance(inner.ctx, ast.Store):
                                diagnostics.append(
                                    Diagnostic(
                                        severity=Severity.ERROR,
                                        message=f"Cannot assign to attribute of capability '{inner.value.id}'",
                                        rule_id="C5",
                                        line=inner.lineno,
                                        column=inner.col_offset,
                                    )
                                )

            ctx.pop_scope()

    return diagnostics
