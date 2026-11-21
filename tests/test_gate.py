from harness.orchestration.gate import gate, Decision


def test_route_on_pass():
    assert gate({"passed": True, "pass_rate": 0.99}) is Decision.ROUTE

def test_quarantine_mid():
    assert gate({"passed": False, "pass_rate": 0.6}) is Decision.QUARANTINE

def test_reject_low():
    assert gate({"passed": False, "pass_rate": 0.1}) is Decision.REJECT