import os
import sys
import csv
import json
import time
import shutil
import hashlib
import argparse
import subprocess
from datetime import datetime

LOOP_DIR = os.path.join("RESEARCH", "kaggle_loop")
SUBMISSIONS_FILE = os.path.join(LOOP_DIR, "submissions.jsonl")
LEADERBOARD_FILE = os.path.join(LOOP_DIR, "leaderboard_history.json")
CHAMPION_FILE = os.path.join(LOOP_DIR, "current_champion.json")
KAGGLE_EXE = os.path.join(".venv", "Scripts", "kaggle.exe") if os.name == 'nt' else "kaggle"

def _run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {' '.join(cmd)}\\n{result.stderr}")
        sys.exit(1)
    return result.stdout

def _sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def status():
    print("Fetching Kaggle Submissions...")
    stdout = _run_cmd([KAGGLE_EXE, "competitions", "submissions", "kaggriculture", "-v"])
    
    import io
    # Parse CSV
    reader = csv.DictReader(io.StringIO(stdout))
    rows = list(reader)
    
    history = []
    champion = {"score": 0.0, "ref": None, "desc": None}
    
    for row in rows:
        try:
            score = float(row.get("publicScore", 0) or 0)
        except ValueError:
            score = 0.0
            
        history.append({
            "ref": row["ref"],
            "date": row["date"],
            "description": row["description"],
            "status": row["status"],
            "publicScore": score
        })
        
        if score > champion["score"]:
            champion = {"score": score, "ref": row["ref"], "desc": row["description"]}
            
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(history, f, indent=2)
        
    with open(CHAMPION_FILE, "w") as f:
        json.dump(champion, f, indent=2)
        
    print(f"Recorded {len(history)} submissions.")
    print(f"Current Champion: {champion['desc']} (Score: {champion['score']})")

def package(agent_path):
    print(f"Packaging {agent_path}...")
    if not os.path.exists(agent_path):
        print(f"Agent path {agent_path} does not exist!")
        sys.exit(1)
        
    # Security Scan
    with open(agent_path, "r") as f:
        content = f.read()
        if "KAGGLE_" in content or "password" in content.lower() or "secret" in content.lower():
            print("WARNING: Possible credentials found in agent code. Review before submission.")
            
    # Copy to main.py
    shutil.copy(agent_path, "main.py")
    
    # Create submission.tar.gz
    _run_cmd(["tar", "-czf", "submission.tar.gz", "main.py"])
    
    main_hash = _sha256("main.py")
    tar_hash = _sha256("submission.tar.gz")
    
    print("Packaging complete.")
    print(f"main.py SHA256: {main_hash}")
    print(f"submission.tar.gz SHA256: {tar_hash}")
    return main_hash, tar_hash

def submit(agent_path, description):
    main_hash, tar_hash = package(agent_path)
    
    print(f"Submitting to Kaggle: {description}")
    _run_cmd([KAGGLE_EXE, "competitions", "submit", "kaggriculture", "-f", "submission.tar.gz", "-m", description])
    
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent_path": agent_path,
        "description": description,
        "main_sha256": main_hash,
        "tar_sha256": tar_hash
    }
    
    with open(SUBMISSIONS_FILE, "a") as f:
        f.write(json.dumps(record) + "\\n")
        
    print("Submission successful. Run 'status' to poll for evaluation.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    
    subparsers.add_parser("status")
    
    pkg_parser = subparsers.add_parser("package")
    pkg_parser.add_argument("--agent", required=True)
    
    sub_parser = subparsers.add_parser("submit")
    sub_parser.add_argument("--agent", required=True)
    sub_parser.add_argument("--hypothesis", required=True)
    
    args = parser.parse_args()
    
    if args.cmd == "status":
        status()
    elif args.cmd == "package":
        package(args.agent)
    elif args.cmd == "submit":
        submit(args.agent, args.hypothesis)
