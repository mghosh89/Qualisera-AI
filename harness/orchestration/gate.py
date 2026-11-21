"""Orchestration gate — the §5.6 'Possible Orchestrated Extension'
brought to life. Consumes a validation result and decides whether a
record reaches the mock API. Policy thresholds are explicit config,
NOT assumed clinical standards (§5.6)."""
from enum import Enum


class Decision(Enum):
    ROUTE = "route"          # passed -> send to API
    QUARANTINE = "quarantine"
    REJECT = "reject"


def gate(validation_result, *, min_pass_rate=0.95):
    """validation_result: dict with keys {passed: bool, pass_rate: float}.
    Returns a Decision. This is the controller the prototype's §3/§5.6
    says is 'not currently wired' — here it is, as an opt-in layer."""
    if validation_result.get("passed") and \
       validation_result.get("pass_rate", 0) >= min_pass_rate:
        return Decision.ROUTE
    if validation_result.get("pass_rate", 0) >= 0.5:
        return Decision.QUARANTINE
    return Decision.REJECT