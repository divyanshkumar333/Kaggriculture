import os
import json
import subprocess
from pathlib import Path

def test_auth():
    kaggle_json_path = Path.home() / ".kaggle" / "kaggle.json"
    access_token_path = Path.home() / ".kaggle" / "access_token"
    
    if kaggle_json_path.exists():
        try:
            with open(kaggle_json_path, "r") as f:
                data = json.load(f)
            if "username" in data and "key" in data:
                os.environ["KAGGLE_USERNAME"] = str(data["username"])
                os.environ["KAGGLE_KEY"] = str(data["key"])
        except Exception:
            pass
            
    # Try calling kaggle CLI with env vars set in process
    res = subprocess.run([
        sys_executable := os.sys.executable,
        "-m", "kaggle", "competitions", "list", "-s", "kaggriculture"
    ], capture_output=True, text=True)
    
    if res.returncode == 0 and "kaggriculture" in res.stdout.lower():
        print("STATUS: AUTHENTICATED")
        print("ACCESS: CONFIRMED")
    else:
        print("STATUS: NOT AUTHENTICATED")
        print("ACCESS: UNKNOWN")

if __name__ == "__main__":
    test_auth()
