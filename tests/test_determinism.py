# tests/test_determinism.py
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

def test_import_time_forbidden_D2():
    src = """
import time

def f() -> int:
    return time.time()
"""
    ids = _diag_ids(src)
    assert ("D2", Severity.ERROR) in ids  # SPEC D2


def test_import_random_forbidden_D2():
    src = """
from random import randint

def f() -> int:
    return randint(0, 10)
"""
    ids = _diag_ids(src)
    assert ("D2", Severity.ERROR) in ids  # SPEC D2


def test_direct_nondeterministic_call_forbidden_D2():
    src = """
import secrets

def f() -> int:
    return secrets.randbelow(10)
"""
    ids = _diag_ids(src)
    assert ("D2", Severity.ERROR) in ids  # SPEC D2


# ----------------------------
# Passing examples (2)
# ----------------------------

def test_deterministic_code_without_time_or_random():
    src = """
def f() -> int:
    x = 1
    y = 2
    return x + y
"""
    ids = _diag_ids(src)
    assert not any(rule_id == "D2" for rule_id, _sev in ids)


def test_for_loop_allowed_not_unbounded():
    src = """
def f() -> int:
    acc = 0
    for i in range(5):
        acc = acc + i
    return acc
"""
    ids = _diag_ids(src)
    assert not any(rule_id == "D1" for rule_id, _sev in ids)
