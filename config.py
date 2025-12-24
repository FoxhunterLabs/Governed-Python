# governed/config.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set


@dataclass(slots=True)
class Config:
    """
    Governed Python configuration.

    This module is intentionally small: it holds configuration only.
    No AST logic and no rule enforcement belongs here.
    """

    # Imports allowed by the checker (root module names only).
    allowed_imports: Set[str] = field(
        default_factory=lambda: {"typing", "dataclasses", "enum", "math", "decimal", "governed"}
    )

    # If strict is False, the engine may downgrade/omit warnings depending on rule modules.
    strict: bool = True

    # Optional knobs that other layers may use (engine/rules), but do not enforce here.
    protocol_validation: str = "strict"   # e.g. "strict" | "lenient"
    secret_protection: str = "strict"     # e.g. "strict" | "lenient"

    # Optional determinism/testing configuration (authoring-level; runtime is out of scope here).
    deterministic_test: bool = False
    test_seed: Optional[int] = 42
