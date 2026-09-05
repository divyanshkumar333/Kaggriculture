import os
import json
import random
from collections import defaultdict
from kaggle_environments import make

# Disable warnings from kaggle_environments
import warnings
warnings.filterwarnings("ignore")

AGENTS = {
    "V027_Base": "agents/v027_hierarchical_meta.py",
    "V028_ImpactOrdering": "agents/v028_notebook_impact_ordering.py",
    "V028_1C4S_Opening": "agents/v028_notebook_1c4s_opening.py"
}

NUM_SEEDS = 10

def play_match(agent_0, agent_1, seed):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "randomSeed": seed}, debug=False)
    env.run([agent_0, agent_1])
    
    final_state = env.steps[-1]
    r0 = final_state[0].reward
    r1 = final_state[1].reward
    
    # Check for structural failures (weeds, starved animals)
    p0_obs = final_state[0].observation.farms[0]
    p1_obs = final_state[0].observation.farms[1]
    
    weeds_0, weeds_1 = 0, 0
    starved_0, starved_1 = 0, 0
    
    for r in range(10):
        for c in range(10):
            t0 = p0_obs.tiles[r][c]
            t1 = p1_obs.tiles[r][c]
            if isinstance(t0, dict):
                if t0.get("kind") == "WEED": weeds_0 += 1
                elif t0.get("consecutive_unfed", 0) > 0: starved_0 += 1
            if isinstance(t1, dict):
                if t1.get("kind") == "WEED": weeds_1 += 1
                elif t1.get("consecutive_unfed", 0) > 0: starved_1 += 1
                
    return (r0, weeds_0, starved_0), (r1, weeds_1, starved_1)

def evaluate_candidate(candidate_name, base_name="V027_Base"):
    print(f"\n{'='*60}")
    print(f"EVALUATING: {candidate_name} vs {base_name}")
    print(f"{'='*60}")
    
    agent_cand = AGENTS[candidate_name]
    agent_base = AGENTS[base_name]
    
    results = []
    
    # Fixed random seeds for paired evaluation
    random.seed(42)
    seeds = [random.randint(1, 999999) for _ in range(NUM_SEEDS)]
    
    wins = 0
    total_delta = 0
    failures = 0
    
    for i, seed in enumerate(seeds):
        # Seat 0: Candidate, Seat 1: Base
        (cand_r0, cw0, cs0), (base_r1, bw1, bs1) = play_match(agent_cand, agent_base, seed)
        delta_0 = cand_r0 - base_r1
        
        # Seat 0: Base, Seat 1: Candidate
        (base_r0, bw0, bs0), (cand_r1, cw1, cs1) = play_match(agent_base, agent_cand, seed)
        delta_1 = cand_r1 - base_r0
        
        paired_delta = delta_0 + delta_1
        total_delta += paired_delta
        
        match_wins = (1 if delta_0 > 0 else 0) + (1 if delta_1 > 0 else 0)
        wins += match_wins
        
        # Check structural integrity
        if cw0 > 0 or cs0 > 0 or cw1 > 0 or cs1 > 0:
            failures += 1
            
        print(f"Seed {seed:6} | Seat 0 Delta: {delta_0:6} | Seat 1 Delta: {delta_1:6} | Paired: {paired_delta:6}")
        results.append(paired_delta)
        
    results.sort()
    p10 = results[int(NUM_SEEDS * 0.1)]
    p90 = results[int(NUM_SEEDS * 0.9)]
    median = results[NUM_SEEDS // 2]
    mean_delta = total_delta / NUM_SEEDS
    
    print("-" * 60)
    print(f"Candidate: {candidate_name}")
    print(f"Win Rate:  {wins}/{NUM_SEEDS*2} ({(wins/(NUM_SEEDS*2))*100:.1f}%)")
    print(f"Failures:  {failures}/{NUM_SEEDS*2} matches had weeds/starvation")
    print(f"Mean Pair: {mean_delta:+.1f} coins")
    print(f"Med Pair:  {median:+.1f} coins")
    print(f"P10/P90:   {p10:+.1f} / {p90:+.1f}")
    
    return {
        "wins": wins,
        "matches": NUM_SEEDS*2,
        "failures": failures,
        "mean": mean_delta,
        "median": median,
        "p10": p10,
        "p90": p90
    }

if __name__ == "__main__":
    results = {}
    for cand in ["V028_ImpactOrdering", "V028_1C4S_Opening"]:
        stats = evaluate_candidate(cand)
        results[cand] = stats
        
    print("\n\nFINAL EVALUATION SUMMARY")
    for cand, stats in results.items():
        print(f"{cand:25} | {stats['wins']:2}/{stats['matches']:2} W | Mean: {stats['mean']:+7.1f} | Failures: {stats['failures']}")
