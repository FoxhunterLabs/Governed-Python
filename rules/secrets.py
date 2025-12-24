# governed/rules/secrets.py
from __future__ import annotations

import ast
from typing import List, Set

from governed.ast.context import Context, Symbol
from governed.diagnostics import Diagnostic, Severity


SECRET_SINKS: Set[str] = {
    "print",
    "str",
    "repr",
    "format",
    "ascii",
    "log",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
}


def _is_secret_annotation(node: ast.AST) -> bool:
    """
    Detect Secret[T] annotations syntactically.
    """
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        return node.value.id == "Secret"
    return False


def check(tree: ast.AST, ctx: Context) -> List[Diagnostic]:
    diagnostics: List[Diagnostic] = []

    for node in ast.walk(tree):

        # SE1 / SE5 — declaring secret-typed variables
        if isinstance(node, ast.AnnAssign):
            if _is_secret_annotation(node.annotation):
                if isinstance(node.target, ast.Name):
                    ctx.current_scope.define(
                        Symbol(
                            name=node.target.id,
                            kind="secret",
                            node=node,
                        )
                    )

        # Track function scopes
        if isinstance(node, ast.FunctionDef):
            ctx.push_scope(f"func:{node.name}")

            # Register secret parameters
            for arg in node.args.args:
                if arg.annotation and _is_secret_annotation(arg.annotation):
                    ctx.current_scope.define(
                        Symbol(
                            name=arg.arg,
                            kind="secret",
                            node=arg,
                        )
                    )

            for inner in ast.walk(node):

                # SE3 — secret to string / interpolation
                if isinstance(inner, ast.JoinedStr):
                    for val in inner.values:
                        if isinstance(val, ast.FormattedValue):
                            if isinstance(val.value, ast.Name):
                                sym = ctx.current_scope.lookup(val.value.id)
                                if sym and sym.kind == "secret":
                                    diagnostics.append(
                                        Diagnostic(
                                            severity=Severity.ERROR,
                                            message="Secret interpolated into f-string",
                                            rule_id="SE3",
                                            line=inner.lineno,
                                            column=inner.col_offset,
                                        )
                                    )

                # SE4 — secret sinks
                if isinstance(inner, ast.Call):
                    if isinstance(inner.func, ast.Name):
                        if inner.func.id in SECRET_SINKS:
                            for arg in inner.args:
                                if isinstance(arg, ast.Name):
                                    sym = ctx.current_scope.lookup(arg.id)
                                    if sym and sym.kind == "secret":
                                        diagnostics.append(
                                            Diagnostic(
                                                severity=Severity.ERROR,
                                                message=f"Secret passed to sink '{inner.func.id}'",
                                                rule_id="SE4",
                                                line=inner.lineno,
                                                column=inner.col_offset,
                                            )
                                        )

                # SE6 — use after consume (simple model: assignment consumes)
                if isinstance(inner, ast.Assign):
                    if isinstance(inner.value, ast.Name):
                        sym = ctx.current_scope.lookup(inner.value.id)
                        if sym and sym.kind == "secret":
                            sym.consumed = True

                if isinstance(inner, ast.Name) and isinstance(inner.ctx, ast.Load):
                    sym = ctx.current_scope.lookup(inner.id)
                    if sym and sym.kind == "secret" and sym.consumed:
                        diagnostics.append(
                            Diagnostic(
                                severity=Severity.ERROR,
                                message=f"Use of consumed secret '{inner.id}'",
                                rule_id="SE6",
                                line=inner.lineno,
                                column=inner.col_offset,
                            )
                        )

            ctx.pop_scope()

    return diagnostics
