# tests/test_secrets.py
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

def test_secret_to_string_forbidden_SE3():
    src = """
def f(key: Secret[int]) -> int:
    s = f"key={key}"
    return 0
"""
    ids = _diag_ids(src)
    assert ("SE3", Severity.ERROR) in ids  # SPEC SE3


def test_secret_sink_print_forbidden_SE4():
    src = """
def f(key: Secret[int]) -> int:
    print(key)
    return 0
"""
    ids = _diag_ids(src)
    assert ("SE4", Severity.ERROR) in ids  # SPEC SE4


def test_secret_use_after_consume_SE6():
    src = """
def f(key: Secret[int]) -> int:
    x = key
    y = key
    return 0
"""
    ids = _diag_ids(src)
    assert ("SE6", Severity.ERROR) in ids  # SPEC SE6


# ----------------------------
# Passing examples (2)
# ----------------------------

def test_secret_not_stringified_or_leaked():
    src = """
def f(key: Secret[int]) -> int:
    x = 1
    return x
"""
    ids = _diag_ids(src)
    assert not any(rule_id in {"SE3", "SE4", "SE6"} for rule_id, _sev in ids)


def test_secret_not_consumed():
    src = """
def f(key: Secret[int]) -> int:
    return 0
"""
    ids = _diag_ids(src)
    assert ("SE6", Severity.ERROR) not in ids
