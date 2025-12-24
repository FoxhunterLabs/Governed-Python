# tests/test_capabilities.py
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

def test_capability_local_declaration_forbidden_C2():
    src = """
def f() -> int:
    clk: Clock = Clock()
    return 0
"""
    ids = _diag_ids(src)
    assert ("C2", Severity.ERROR) in ids  # SPEC C2


def test_capability_return_forbidden_C3():
    src = """
def f(clk: Clock) -> Clock:
    return clk
"""
    ids = _diag_ids(src)
    assert ("C3", Severity.ERROR) in ids  # SPEC C3


def test_capability_use_after_consume_C4():
    src = """
def f(clk: Clock) -> int:
    x = clk
    y = clk
    return 0
"""
    ids = _diag_ids(src)
    assert ("C4", Severity.ERROR) in ids  # SPEC C4


# ----------------------------
# Passing examples (2)
# ----------------------------

def test_capability_valid_parameter_use():
    src = """
def f(clk: Clock) -> int:
    t = 1
    return t
"""
    ids = _diag_ids(src)
    assert not any(rule_id in {"C2", "C3", "C4", "C5"} for rule_id, _sev in ids)


def test_capability_not_returned():
    src = """
def f(rng: Rng) -> int:
    x = 1
    return x
"""
    ids = _diag_ids(src)
    assert ("C3", Severity.ERROR) not in ids
