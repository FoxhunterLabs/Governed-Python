# governed/rules/syntax.py
from __future__ import annotations

import ast
from typing import List

from governed.ast.context import Context
from governed.diagnostics import Diagnostic, Severity


# AST node types forbidden by SPEC §1
BANNED_NODES = (
    ast.While,
    ast.Try,
    ast.Raise,
    ast.Lambda,
    ast.AsyncFunctionDef,
    ast.Await,
    ast.Yield,
    ast.YieldFrom,
    ast.With,
    ast.GeneratorExp,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
)

# Mutable literals forbidden by SPEC §1
BANNED_LITERALS = (
    ast.List,
    ast.Dict,
    ast.Set,
)


def check(tree: ast.AST, ctx: Context) -> List[Diagnostic]:
    diagnostics: List[Diagnostic] = []

    for node in ast.walk(tree):

        # S1 — forbidden control flow and expressions
        if isinstance(node, BANNED_NODES):
            diagnostics.append(
                Diagnostic(
                    severity=Severity.ERROR,
                    message=f"Use of {type(node).__name__} is forbidden in Governed Python",
                    rule_id="S1",
                    line=getattr(node, "lineno", None),
                    column=getattr(node, "col_offset", None),
                )
            )

        # S2 — forbidden mutable literals
        if isinstance(node, BANNED_LITERALS):
            diagnostics.append(
                Diagnostic(
                    severity=Severity.ERROR,
                    message=f"Mutable literal {type(node).__name__} is forbidden",
                    rule_id="S2",
                    suggestion="Use tuple, Vector, or Map instead",
                    line=getattr(node, "lineno", None),
                    column=getattr(node, "col_offset", None),
                )
            )

        # S4 — match must include wildcard case
        if isinstance(node, ast.Match):
            has_wildcard = any(
                isinstance(case.pattern, ast.MatchAs)
                and case.pattern.name is None
                for case in node.cases
            )
            if not has_wildcard:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message="match statement must include a wildcard (case _)",
                        rule_id="S4",
                        line=node.lineno,
                        column=node.col_offset,
                    )
                )

        # S6 — import restrictions
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in ctx.config.allowed_imports:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            message=f"Import '{alias.name}' is not allowed",
                            rule_id="S6",
                            line=node.lineno,
                            column=node.col_offset,
                        )
                    )

        if isinstance(node, ast.ImportFrom):
            if node.module is None:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        message="Relative imports are forbidden",
                        rule_id="S6",
                        line=node.lineno,
                        column=node.col_offset,
                    )
                )
            else:
                root = node.module.split(".")[0]
                if root not in ctx.config.allowed_imports:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            message=f"Import from '{node.module}' is not allowed",
                            rule_id="S6",
                            line=node.lineno,
                            column=node.col_offset,
                        )
                    )

    return diagnostics
