import os
import glob
import subprocess
import json
import itertools
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROMOTED_DIR = ROOT / "RESEARCH" / "promoted"
META_DIR = ROOT / "RESEARCH" / "meta"
BENCH_SCRIPT = ROOT / "scripts" / "bench_paired.py"

def get_agents():
    agents = [str(ROOT / "main.py")]
    if PROMOTED_DIR.exists():
        for p in glob.glob(str(PROMOTED_DIR / "*.py")):
            agents.append(p)
    return agents

def main():
    agents = get_agents()
    print(f"Found {len(agents)} agents for compatibility graph.")
    
    matrix = {}
    
    # We only need to compute combinations, not permutations, since bench_paired does both seats.
    # But for a full directed graph where A->B is A's winrate vs B, A vs B is the same match as B vs A
    # bench_paired returns the paired win rate of A. The win rate of B is 1 - A_win_rate (ignoring ties).
    
    pairs = list(itertools.combinations(agents, 2))
    print(f"Total pairs to evaluate: {len(pairs)}")
    
    for agent_a, agent_b in pairs:
        name_a = Path(agent_a).stem
        name_b = Path(agent_b).stem
        
        print(f"\nRunning {name_a} vs {name_b}...")
        cmd = [
            sys.executable,
            str(BENCH_SCRIPT),
            agent_a,
            agent_b,
            "--seeds", "8"
        ]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            # Find the JSON output block at the end
            out = res.stdout.strip().split("\n")
            json_str = ""
            in_json = False
            for line in out:
                if line.startswith("{"):
                    in_json = True
                if in_json:
                    json_str += line + "\n"
                if line.startswith("}"):
                    break
                    
            if not json_str:
                print(f"Error parsing JSON from output.")
                continue
                
            data = json.loads(json_str)
            if name_a not in matrix:
                matrix[name_a] = {}
            if name_b not in matrix:
                matrix[name_b] = {}
                
            matrix[name_a][name_b] = {
                "win_rate": data["paired_win_rate"],
                "mean_delta": data["mean_delta"]
            }
            matrix[name_b][name_a] = {
                "win_rate": 1.0 - data["paired_win_rate"],
                "mean_delta": -data["mean_delta"]
            }
            
        except subprocess.CalledProcessError as e:
            print(f"Error running {name_a} vs {name_b}: {e}")
            print(e.stderr)
            
    META_DIR.mkdir(parents=True, exist_ok=True)
    out_json = META_DIR / "compatibility_graph.json"
    
    with open(out_json, "w") as f:
        json.dump(matrix, f, indent=2)
        
    print(f"\nWrote compatibility graph to {out_json}")
    
    # Generate Markdown Table
    out_md = META_DIR / "compatibility_matrix.md"
    agent_names = sorted(list(matrix.keys()))
    
    with open(out_md, "w") as f:
        f.write("# Policy Compatibility Matrix\n\n")
        
        # Header
        f.write("| Agent | " + " | ".join(agent_names) + " |\n")
        f.write("|---|" + "|".join(["---" for _ in agent_names]) + "|\n")
        
        for a in agent_names:
            row = [a]
            for b in agent_names:
                if a == b:
                    row.append("-")
                elif b in matrix.get(a, {}):
                    wr = matrix[a][b]['win_rate']
                    delta = matrix[a][b]['mean_delta']
                    row.append(f"{wr*100:.0f}% (d={delta:+.0f})")
                else:
                    row.append("N/A")
            f.write("| " + " | ".join(row) + " |\n")
            
    print(f"Wrote Markdown matrix to {out_md}")

if __name__ == "__main__":
    import sys
    main()
