import sys
import os
import json
from fast_tournament import run_fast_tournament

if __name__ == '__main__':
    cand_path = sys.argv[1]
    opp_path = sys.argv[2]
    num_seeds = int(sys.argv[3])
    
    seeds = [1337 + i for i in range(num_seeds)]
    summary, overall_wr, overall_margin = run_fast_tournament(cand_path, [opp_path], seeds=seeds, max_workers=6)
    
    wins = summary[os.path.basename(opp_path)]["wins"]
    losses = summary[os.path.basename(opp_path)]["losses"]
    
    result = {"wins": wins, "losses": losses, "margin": overall_margin}
    with open(os.path.join(os.path.dirname(cand_path), "result.json"), "w") as f:
        json.dump(result, f)
