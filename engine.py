# governed/engine.py
from __future__ import annotations

import ast
from typing import List

from governed.config import Config
from governed.diagnostics import Diagnostic
from governed.ast.context import Context

# Import rule modules (implemented later)
from governed.rules import (
    syntax,
    capabilities,
    secrets,
    protocol,
    determinism,
)


class CheckerEngine:
    """
    Orchestrates static checking for Governed Python.

    This engine contains NO rule logic.
    It only:
      - constructs context
      - parses the AST
      - runs rule modules in a fixed order
      - aggregates diagnostics
    """

    def __init__(self, config: Config):
        self.config = config

    def check(self, tree: ast.AST) -> List[Diagnostic]:
        """
        Run all checker rules against the given AST.
        """
        ctx = Context(config=self.config)
        diagnostics: List[Diagnostic] = []

        # Rule execution order is fixed and deterministic.
        # Each rule module is responsible for exactly its SPEC scope.
        rule_modules = [
            syntax,
            capabilities,
            secrets,
            protocol,
            determinism,
        ]

        for module in rule_modules:
            if hasattr(module, "check"):
                diags = module.check(tree, ctx)
                if diags:
                    diagnostics.extend(diags)

        return diagnostics


def check_source(source: str, config: Config) -> List[Diagnostic]:
    """
    Convenience helper: parse source and run the checker.
    """
    tree = ast.parse(source)
    engine = CheckerEngine(config)
    return engine.check(tree)
