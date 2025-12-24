# governed/ast/context.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any


@dataclass
class Symbol:
    """
    A symbol bound in a scope.

    This represents names introduced by assignments, parameters,
    functions, classes, or protocol states.
    """
    name: str
    kind: str  # e.g. "variable", "parameter", "function", "class", "state"
    node: Any

    # Optional semantic flags used by rules
    consumed: bool = False


class Scope:
    """
    Lexical scope with parent linkage.
    """

    def __init__(self, name: str, parent: Optional[Scope] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List[Scope] = []

        if parent is not None:
            parent.children.append(self)

    def define(self, symbol: Symbol) -> None:
        """
        Define a symbol in the current scope.
        """
        self.symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol in this scope or any parent scope.
        """
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """
        Look up a symbol only in the current scope.
        """
        return self.symbols.get(name)


@dataclass
class Context:
    """
    Shared checker context passed to all rule modules.

    This object is mutated as the AST is traversed.
    It contains no rule logic itself.
    """

    config: Any

    # Scope tracking
    global_scope: Scope = field(default_factory=lambda: Scope("global"))
    current_scope: Scope = field(init=False)

    # Protocol models collected by protocol rules
    protocols: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.current_scope = self.global_scope

    # ---- scope management helpers ----

    def push_scope(self, name: str) -> None:
        self.current_scope = Scope(name, parent=self.current_scope)

    def pop_scope(self) -> None:
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent
