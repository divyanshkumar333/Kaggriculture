"""
Multi-opponent tournament for v090_meta_adaptive.
Runs v090 against 5 opponents, both seat orders.
Records: wins, losses, draws, mean cash.
"""
from kaggle_environments import make
import statistics

OPPONENTS = [
    "random",
    "agents/v057_generalized_spoiler.py",
    "agents/013_robust_trace.py",
    "agents/v013_robust_trace.py",
]

def run_match(a1, a2):
    env = make('kaggriculture', configuration={'episodeSteps': 720}, debug=False)
    env.run([a1, a2])
    final = env.steps[-1]
    return final[0].reward, final[1].reward

def main():
    agent = "agents/v090_meta_adaptive.py"
    print(f"=== TOURNAMENT: {agent} ===\n")
    
    wins = 0; losses = 0; draws = 0
    our_scores = []
    
    for opp in OPPONENTS:
        # Both seat orders
        for order in [(agent, opp), (opp, agent)]:
            r0, r1 = run_match(*order)
            if order[0] == agent:
                our_r, opp_r = r0, r1
            else:
                our_r, opp_r = r1, r0
            
            result = "WIN" if our_r > opp_r else ("DRAW" if our_r == opp_r else "LOSS")
            if result == "WIN": wins += 1
            elif result == "LOSS": losses += 1
            else: draws += 1
            our_scores.append(our_r)
            
            opp_name = opp.split('/')[-1] if '/' in opp else opp
            print(f"  {opp_name} | {result} | us={our_r:.0f} opp={opp_r:.0f}")
    
    print(f"\nSummary: {wins}W / {losses}L / {draws}D")
    print(f"Our scores: mean={statistics.mean(our_scores):.0f} median={statistics.median(our_scores):.0f} min={min(our_scores):.0f} max={max(our_scores):.0f}")

if __name__ == "__main__":
    main()
