"""
Comprehensive benchmark: v092b seed and v093_evolved_best vs 4-opponent ensemble, both seats.
This is the go/no-go decision for tomorrow's submission.
"""
from kaggle_environments import make
import statistics

AGENTS = {
    "013_baseline": "agents/013_robust_trace.py",
    "v092b_seed":   "agents/v092b_replay_seed.py",
    "v093_best":    "agents/v093_evolved_best.py",
}

OPPONENTS = [
    ("v057", "agents/v057_generalized_spoiler.py"),
    ("013",  "agents/013_robust_trace.py"),
    ("rand", "random"),
]

def run(a1, a2):
    env = make('kaggriculture', configuration={'episodeSteps': 720}, debug=False)
    env.run([a1, a2])
    f = env.steps[-1]
    return f[0].reward, f[1].reward

results = {}
for name, path in AGENTS.items():
    wins = 0; losses = 0; scores = []
    for opp_name, opp_path in OPPONENTS:
        if path == opp_path: continue  # skip self-match
        # As P0
        r0, r1 = run(path, opp_path)
        wins += (1 if r0 > r1 else 0); losses += (1 if r0 < r1 else 0)
        scores.append(r0)
        print(f"  {name}(P0) vs {opp_name}: us={r0:.0f} opp={r1:.0f} {'WIN' if r0 > r1 else 'LOSS'}")
        # As P1
        r0, r1 = run(opp_path, path)
        wins += (1 if r1 > r0 else 0); losses += (1 if r1 < r0 else 0)
        scores.append(r1)
        print(f"  {name}(P1) vs {opp_name}: us={r1:.0f} opp={r0:.0f} {'WIN' if r1 > r0 else 'LOSS'}")
    
    mean_sc = statistics.mean(scores)
    results[name] = {"wins": wins, "losses": losses, "mean": mean_sc, "scores": scores}
    print(f"  => {name}: {wins}W/{losses}L mean={mean_sc:.0f} min={min(scores):.0f}\n")

print("\n=== SUMMARY ===")
for name, r in sorted(results.items(), key=lambda x: x[1]['mean'], reverse=True):
    wr = r['wins'] / (r['wins'] + r['losses'])
    print(f"  {name:20s}: {r['wins']}W/{r['losses']}L WR={wr:.0%} mean={r['mean']:.0f} min={min(r['scores']):.0f}")
