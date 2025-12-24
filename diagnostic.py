# governed/diagnostics.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class Severity(Enum):
    """
    Diagnostic severity levels.

    Values are ordered from most to least severe.
    """
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass(frozen=True)
class Diagnostic:
    """
    A single diagnostic produced by the checker.

    This object is deliberately dumb:
    it contains data only, no checker logic.
    """

    severity: Severity
    message: str

    # Optional metadata
    rule_id: Optional[str] = None
    suggestion: Optional[str] = None

    # Source location
    line: Optional[int] = None
    column: Optional[int] = None
    end_line: Optional[int] = None
    end_column: Optional[int] = None

    def to_json(self) -> Dict[str, Any]:
        """
        Convert diagnostic to a JSON-serializable structure.
        Intended for IDEs and tooling.
        """
        return {
            "severity": self.severity.value,
            "message": self.message,
            "rule_id": self.rule_id,
            "suggestion": self.suggestion,
            "range": {
                "start": {
                    "line": self.line or 0,
                    "column": self.column or 0,
                },
                "end": {
                    "line": self.end_line or self.line or 0,
                    "column": self.end_column or self.column or 0,
                },
            },
        }

    def format_human(self) -> str:
        """
        Render a human-readable diagnostic string.
        """
        loc = ""
        if self.line is not None:
            loc = f" (line {self.line}, col {self.column or 0})"

        header = self.severity.value.upper()
        if self.rule_id:
            header += f" [{self.rule_id}]"

        output = f"{header}: {self.message}{loc}"

        if self.suggestion:
            output += f"\n  → Suggestion: {self.suggestion}"

        return output
