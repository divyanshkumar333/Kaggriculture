import json
import os
import sys
import time
from kaggle_environments import make

def load_agent(agent_path):
    namespace = {}
    with open(agent_path, "r", encoding="utf-8") as f:
        code = f.read()
    exec(compile(code, os.path.basename(agent_path), "exec"), namespace)
    # Return last callable in namespace (Kaggle evaluator convention)
    callables = [v for v in namespace.values() if callable(v)]
    if not callables:
        raise ValueError(f"No callable found in {agent_path}")
    return callables[-1]

def run_match(agent0, agent1, seed):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    env.run([agent0, agent1])
    last = env.steps[-1]
    rew0 = last[0].get("reward", 0)
    rew1 = last[1].get("reward", 0)
    status0 = last[0].get("status", "UNKNOWN")
    status1 = last[1].get("status", "UNKNOWN")
    return rew0, rew1, status0, status1

def run_tournament(candidate_path, population_paths, seeds=[42, 101, 2024, 777, 9999]):
    print(f"=== TOURNAMENT EVALUATION ===")
    print(f"Candidate: {candidate_path}")
    print(f"Population: {len(population_paths)} opponents")
    print(f"Seeds: {seeds}")
    
    cand_agent = load_agent(candidate_path)
    
    summary = {}
    total_wins = 0
    total_losses = 0
    total_draws = 0
    total_margin = 0
    total_games = 0
    
    for opp_path in population_paths:
        opp_name = os.path.basename(opp_path)
        opp_agent = load_agent(opp_path)
        opp_wins = 0
        opp_losses = 0
        opp_draws = 0
        opp_margins = []
        
        for seed in seeds:
            # Candidate as P0
            r0, r1, s0, s1 = run_match(cand_agent, opp_agent, seed)
            margin0 = r0 - r1
            opp_margins.append(margin0)
            if margin0 > 0: opp_wins += 1
            elif margin0 < 0: opp_losses += 1
            else: opp_draws += 1
            
            # Candidate as P1 (Seat swap)
            r0, r1, s0, s1 = run_match(opp_agent, cand_agent, seed)
            margin1 = r1 - r0
            opp_margins.append(margin1)
            if margin1 > 0: opp_wins += 1
            elif margin1 < 0: opp_losses += 1
            else: opp_draws += 1
            
        games = len(seeds) * 2
        total_games += games
        total_wins += opp_wins
        total_losses += opp_losses
        total_draws += opp_draws
        avg_margin = sum(opp_margins) / len(opp_margins)
        total_margin += sum(opp_margins)
        
        wr = (opp_wins / games) * 100
        print(f"vs {opp_name:30} | {opp_wins:2d}W - {opp_losses:2d}L - {opp_draws:2d}D ({wr:5.1f}%) | Mean Margin: {avg_margin:+9.0f}")
        summary[opp_name] = {
            "wins": opp_wins,
            "losses": opp_losses,
            "draws": opp_draws,
            "win_rate": wr,
            "mean_margin": avg_margin
        }
        
    overall_wr = (total_wins / total_games) * 100
    overall_avg_margin = total_margin / total_games
    print("=" * 60)
    print(f"OVERALL: {total_wins}W - {total_losses}L - {total_draws}D ({overall_wr:5.1f}%) | Mean Margin: {overall_avg_margin:+9.0f}")
    return summary, overall_wr, overall_avg_margin

if __name__ == "__main__":
    cand = sys.argv[1] if len(sys.argv) > 1 else r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py"
    pop = [
        r"e:\Setup\kaggle\kaggriculture\submission_v057_control.py",
        r"e:\Setup\kaggle\kaggriculture\agents\public_v16_rc5.py",
        r"e:\Setup\kaggle\kaggriculture\agents\013_robust_trace.py",
        r"e:\Setup\kaggle\kaggriculture\agents\v081_kaggle_83k_trace.py"
    ]
    run_tournament(cand, pop)
