# tests/test_syntax.py
import pytest

from governed.config import Config
from governed.engine import check_source
from governed.diagnostics import Severity


def _diag_ids(src: str):
    diags = check_source(src, Config())
    return {(d.rule_id, d.severity) for d in diags}


# ----------------------------
# Failing examples (3)
# ----------------------------

def test_syntax_bans_while_S1():
    src = """
def f() -> int:
    x: int = 0
    while x < 3:
        x = x + 1
    return x
"""
    ids = _diag_ids(src)
    assert ("S1", Severity.ERROR) in ids  # SPEC S1


def test_syntax_bans_mutable_list_literal_S2():
    src = """
def f() -> int:
    xs = [1, 2, 3]
    return 0
"""
    ids = _diag_ids(src)
    assert ("S2", Severity.ERROR) in ids  # SPEC S2


def test_syntax_requires_match_wildcard_S4():
    src = """
def f(x: int) -> int:
    match x:
        case 1:
            return 10
    return 0
"""
    ids = _diag_ids(src)
    assert ("S4", Severity.ERROR) in ids  # SPEC S4


# ----------------------------
# Passing examples (2)
# ----------------------------

def test_syntax_allows_for_loop_and_tuple():
    src = """
def f() -> int:
    acc: int = 0
    for i in range(3):
        acc = acc + i
    t = (1, 2, 3)
    return acc + t[0]
"""
    ids = _diag_ids(src)
    # No syntax rule violations expected
    assert not any(rule_id in {"S1", "S2", "S4", "S6"} for rule_id, _sev in ids)


def test_syntax_allows_match_with_wildcard():
    src = """
def f(x: int) -> int:
    match x:
        case 1:
            return 10
        case _:
            return 0
"""
    ids = _diag_ids(src)
    assert ("S4", Severity.ERROR) not in ids
