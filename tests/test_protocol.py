# tests/test_protocol.py
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

def test_protocol_missing_states_P3():
    src = """
@protocol
class EmptyProto:
    pass
"""
    ids = _diag_ids(src)
    assert ("P3", Severity.ERROR) in ids  # SPEC P3


def test_transition_unknown_state_P7():
    src = """
@protocol
class BadProto:

    @state
    class Start:
        pass

    @transition(from_=Start, to=Missing)
    def go(s: Start) -> Result[Ok[Start], Err[str]]:
        return Ok(s)
"""
    ids = _diag_ids(src)
    assert ("P7", Severity.ERROR) in ids  # SPEC P7


def test_transition_wrong_return_type_P5():
    src = """
@protocol
class BadReturn:

    @state
    class Start:
        pass

    @transition(from_=Start, to=Start)
    def go(s: Start) -> int:
        return 1
"""
    ids = _diag_ids(src)
    assert ("P5", Severity.ERROR) in ids  # SPEC P5


# ----------------------------
# Passing examples (2)
# ----------------------------

def test_valid_protocol_with_transition():
    src = """
@protocol
class GoodProto:

    @state
    class Start:
        pass

    @state
    class End:
        pass

    @transition(from_=Start, to=End)
    def go(s: Start) -> Result[Ok[End], Err[str]]:
        return Ok(GoodProto.End())
"""
    ids = _diag_ids(src)
    assert not any(rule_id in {"P3", "P5", "P7"} for rule_id, _sev in ids)


def test_protocol_unreachable_state_warns_P8():
    src = """
@protocol
class WarnProto:

    @state
    class Start:
        pass

    @state
    class Never:
        pass

    @transition(from_=Start, to=Start)
    def loop(s: Start) -> Result[Ok[Start], Err[str]]:
        return Ok(s)
"""
    ids = _diag_ids(src)
    assert ("P8", Severity.WARNING) in ids  # SPEC P8
