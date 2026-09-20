import sys
import os
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).parent.parent

def check_file_exists(filepath):
    if not os.path.exists(filepath):
        print(f"[FAIL] Missing file: {filepath}")
        return False
    return True

def get_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def verify_main_py_matches(candidate_path):
    main_hash = get_hash(ROOT / "main.py")
    cand_hash = get_hash(candidate_path)
    if main_hash != cand_hash:
        print("[FAIL] main.py does not match the candidate file exactly.")
        print("       You must copy the candidate to main.py before submission.")
        return False
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/submission_gate.py <candidate_path> <experiment_results.json>")
        sys.exit(1)

    candidate_path = Path(sys.argv[1])
    results_path = Path(sys.argv[2])

    print(f"=== KAGGRICULTURE SUBMISSION FIREWALL ===")
    print(f"Candidate: {candidate_path}")
    print(f"Results File: {results_path}")
    
    passed = True

    # H. Package contains correct main.py
    if not verify_main_py_matches(candidate_path):
        passed = False
        
    # Check results file
    if not check_file_exists(results_path):
        passed = False
    else:
        with open(results_path, 'r') as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                print("[FAIL] Invalid JSON in results file.")
                sys.exit(1)
        
        # A. Smoke
        if not results.get("passed_smoke", False):
            print("[FAIL] Candidate did not pass smoke tests.")
            passed = False
            
        # B. Validation
        if not results.get("passed_validation", False):
            print("[FAIL] Candidate did not pass validation tests.")
            passed = False
            
        # C. Beat Champion
        wr = results.get("win_rate_vs_champion", 0)
        if wr <= 0.50:
            print(f"[FAIL] Candidate did not beat current champion (Win Rate: {wr*100}%)")
            passed = False
            
        # D. No Regression
        if results.get("severe_regression", True):
            print("[FAIL] Severe matchup regression detected.")
            passed = False
            
        # E. Both Seats
        if not results.get("both_seats_tested", False):
            print("[FAIL] Candidate was not tested on both seats (Player 0 and Player 1).")
            passed = False
            
        # F. Current Meta
        if not results.get("current_meta_tested", False):
            print("[FAIL] Candidate was not tested against current meta.")
            passed = False
            
        # G. Adversarial Meta
        if not results.get("adversarial_meta_tested", False):
            print("[FAIL] Candidate was not tested against adversarial meta.")
            passed = False
            
        # J. Registry Entry
        if not results.get("registry_entry", False):
            print("[FAIL] Experiment lacks a registry entry.")
            passed = False

    # I. Runtime Dependencies Verified
    # Very basic check for syntax/imports
    try:
        import py_compile
        py_compile.compile(candidate_path, doraise=True)
    except Exception as e:
        print(f"[FAIL] Syntax/Dependency error in candidate: {e}")
        passed = False

    # K. Hash recorded
    cand_hash = get_hash(candidate_path)
    print(f"[INFO] Candidate Hash: {cand_hash}")

    print("\n-----------------------------------------")
    if passed:
        print("          SUBMISSION APPROVED")
        print("-----------------------------------------")
        sys.exit(0)
    else:
        print("          SUBMISSION BLOCKED")
        print("-----------------------------------------")
        sys.exit(1)

if __name__ == "__main__":
    main()
