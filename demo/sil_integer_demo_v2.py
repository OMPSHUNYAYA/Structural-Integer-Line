# ============================================================
# SIL — Structural Integer Line (v2)
# The Integer Line Is Not Flat
# Deterministic Structural Resolution Demo (ID-Based)
# ============================================================

from typing import List, Dict, Any
import hashlib
import json


# ------------------------------------------------------------
# STRUCTURAL RESOLVER (ID-BASED — ORDER INDEPENDENT)
# ------------------------------------------------------------

def resolve_structure(fragments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Resolve integer position from unordered structural fragments.
    No time. No order. No synchronization.
    Uses ID-based structural pairing.
    """

    base = None
    moves = {}       # id -> value
    retracted = set()
    confirmed = False

    for f in fragments:
        t = f.get("type")

        if t == "OPEN":
            if "value" not in f:
                return {"state": "ABSTAIN", "position": None}
            base = f["value"]

        elif t == "MOVE":
            if "id" not in f or "value" not in f:
                return {"state": "ABSTAIN", "position": None}
            move_id = f["id"]
            moves[move_id] = f["value"]

        elif t == "RETRACT":
            if "target" not in f:
                return {"state": "ABSTAIN", "position": None}
            target = f["target"]
            retracted.add(target)

        elif t == "CONFIRM":
            confirmed = True

        else:
            return {"state": "ABSTAIN", "position": None}

    # -------------------------------
    # VALIDATION
    # -------------------------------

    if base is None:
        return {"state": "INCOMPLETE", "position": None}

    # Apply structural cancellation
    valid_moves = []
    for mid, val in moves.items():
        if mid not in retracted:
            valid_moves.append(val)

    if len(valid_moves) == 0:
        return {"state": "INCOMPLETE", "position": None}

    if len(valid_moves) > 1:
        return {"state": "ABSTAIN", "position": None}

    final_position = base + valid_moves[0]

    if not confirmed:
        return {"state": "INCOMPLETE", "position": final_position}

    return {"state": "RESOLVED", "position": final_position}


# ------------------------------------------------------------
# TEST RUNNER
# ------------------------------------------------------------

def run_test(name: str, fragments: List[Dict[str, Any]]):
    result = resolve_structure(fragments)

    cert_input = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    cert = hashlib.sha256(cert_input).hexdigest()

    print("===================================================")
    print(f"TEST: {name}")
    print("---------------------------------------------------")
    print("Fragments (unordered):")
    for f in fragments:
        print(f"  {f}")
    print("---------------------------------------------------")
    print(f"Result: {result}")
    print(f"Certificate: {cert}")
    print("===================================================\n")

    return result, cert


# ------------------------------------------------------------
# MAIN EXECUTION
# ------------------------------------------------------------

if __name__ == "__main__":

    # --------------------------------------------------------
    # BASE STRUCTURE (IDENTICAL MEANING, DIFFERENT ORDER)
    # --------------------------------------------------------

    fragments_A = [
        {"type": "OPEN", "value": 0},
        {"type": "MOVE", "id": 1, "value": 2},
        {"type": "RETRACT", "target": 1},
        {"type": "MOVE", "id": 2, "value": 3},
        {"type": "CONFIRM"},
    ]

    fragments_B = [
        {"type": "CONFIRM"},
        {"type": "MOVE", "id": 2, "value": 3},
        {"type": "RETRACT", "target": 1},
        {"type": "MOVE", "id": 1, "value": 2},
        {"type": "OPEN", "value": 0},
    ]

    fragments_C = [
        {"type": "MOVE", "id": 1, "value": 2},
        {"type": "OPEN", "value": 0},
        {"type": "MOVE", "id": 2, "value": 3},
        {"type": "RETRACT", "target": 1},
        {"type": "CONFIRM"},
    ]

    # --------------------------------------------------------
    # RUN TESTS
    # --------------------------------------------------------

    r1, c1 = run_test("Node A", fragments_A)
    r2, c2 = run_test("Node B", fragments_B)
    r3, c3 = run_test("Node C", fragments_C)

    # --------------------------------------------------------
    # GLOBAL INVARIANT CHECK
    # --------------------------------------------------------

    print("GLOBAL INVARIANT CHECK")
    print("---------------------------------------------------")

    same_result = (r1 == r2 == r3)
    same_cert = (c1 == c2 == c3)

    print(f"Same Result Across Nodes : {same_result}")
    print(f"Same Certificate        : {same_cert}")

    if same_result and same_cert:
        print("\n✅ STRUCTURAL CONVERGENCE ACHIEVED")
    else:
        print("\n❌ STRUCTURAL DIVERGENCE DETECTED")

    # --------------------------------------------------------
    # OPTIONAL: ABSTAIN TEST (CONFLICT)
    # --------------------------------------------------------

    print("\nABSTAIN TEST (Conflict Scenario)")
    print("---------------------------------------------------")

    conflict_fragments = [
        {"type": "OPEN", "value": 0},
        {"type": "MOVE", "id": 1, "value": 2},
        {"type": "MOVE", "id": 2, "value": 3},
        {"type": "CONFIRM"},
    ]

    run_test("Conflict Case", conflict_fragments)

    # --------------------------------------------------------
    # OPTIONAL: INCOMPLETE TEST
    # --------------------------------------------------------

    print("\nINCOMPLETE TEST (Missing Confirm)")
    print("---------------------------------------------------")

    incomplete_fragments = [
        {"type": "OPEN", "value": 0},
        {"type": "MOVE", "id": 2, "value": 3},
    ]

    run_test("Incomplete Case", incomplete_fragments)