# governed/rules/determinism.py
from __future__ import annotations

import ast
from typing import List, Set

from governed.ast.context import Context
from governed.diagnostics import Diagnostic, Severity


# Names that represent nondeterministic authority
NONDETERMINISTIC_NAMES: Set[str] = {
    "time",
    "random",
    "secrets",
}


def check(tree: ast.AST, ctx: Context) -> List[Diagnostic]:
    diagnostics: List[Diagnostic] = []

    for node in ast.walk(tree):

        # D1 — unbounded loops are forbidden
        # (while is already banned in syntax, but this guards redundancy)
        if isinstance(node, ast.While):
            diagnostics.append(
                Diagnostic(
                    severity=Severity.ERROR,
                    message="Unbounded loops are forbidden",
                    rule_id="D1",
                    line=node.lineno,
                    column=node.col_offset,
                )
            )

        # D2 — direct access to nondeterminism without capability
        if isinstance(node, ast.Call):
            # function call like time.time(), random.randint(), secrets.token_bytes()
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    root = node.func.value.id
                    if root in NONDETERMINISTIC_NAMES:
                        diagnostics.append(
                            Diagnostic(
                                severity=Severity.ERROR,
                                message=f"Nondeterministic access via '{root}' requires an explicit capability",
                                rule_id="D2",
                                suggestion="Use Clock or Rng capabilities instead",
                                line=node.lineno,
                                column=node.col_offset,
                            )
                        )

        # D2 — importing nondeterministic modules
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in NONDETERMINISTIC_NAMES:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            message=f"Import of nondeterministic module '{root}' is forbidden",
                            rule_id="D2",
                            line=node.lineno,
                            column=node.col_offset,
                        )
                    )

        if isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                if root in NONDETERMINISTIC_NAMES:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            message=f"Import from nondeterministic module '{root}' is forbidden",
                            rule_id="D2",
                            line=node.lineno,
                            column=node.col_offset,
                        )
                    )

    return diagnostics
