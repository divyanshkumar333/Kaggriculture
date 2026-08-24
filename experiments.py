import argparse
import sys
import json
import os
import importlib.util
from datetime import datetime
from kaggle_environments import make
import numpy as np

def load_agent_from_file(filepath):
    spec = importlib.util.spec_from_file_location("agent_module", filepath)
    if spec is None:
        return filepath # Might be a built-in like "random" or "pass"
    agent_module = importlib.util.module_from_spec(spec)
    sys.modules["agent_module"] = agent_module
    spec.loader.exec_module(agent_module)
    return getattr(agent_module, "agent")

def main():
    parser = argparse.ArgumentParser(description="Run Kaggriculture experiments.")
    parser.add_argument("--agent", type=str, required=True, help="Path to your agent.py, or built-in (e.g. random)")
    parser.add_argument("--opponent", type=str, default="random", help="Path to opponent agent, or built-in")
    parser.add_argument("--games", type=int, default=10, help="Number of games to run")
    parser.add_argument("--steps", type=int, default=720, help="Number of steps per game")
    parser.add_argument("--seed_start", type=int, default=42, help="Starting seed for deterministic runs")
    parser.add_argument("--output", type=str, default="experiments/results.json", help="Path to output JSON")
    
    args = parser.parse_args()
    
    try:
        agent1 = load_agent_from_file(args.agent) if args.agent not in ["random", "pass", "starter"] else args.agent
        agent2 = load_agent_from_file(args.opponent) if args.opponent not in ["random", "pass", "starter"] else args.opponent
    except Exception as e:
        print(f"Error loading agents: {e}")
        return

    results = {
        "timestamp": datetime.now().isoformat(),
        "agent1": args.agent,
        "agent2": args.opponent,
        "games": args.games,
        "steps": args.steps,
        "seed_start": args.seed_start,
        "wins_a1": 0,
        "wins_a2": 0,
        "ties": 0,
        "errors": 0,
        "a1_rewards": [],
        "a2_rewards": [],
        "game_logs": []
    }

    print(f"Running {args.games} games: {args.agent} vs {args.opponent}")

    for i in range(args.games):
        seed = args.seed_start + i
        config = {"episodeSteps": args.steps, "seed": seed}
        env = make("kaggriculture", configuration=config, debug=False)
        
        # Set environment variable so the agent can read the current seed for metrics tracking
        if "KAGGRICULTURE_SEED" not in os.environ:
            os.environ["KAGGRICULTURE_SEED"] = str(seed)
        
        try:
            # Swap order every other game to ensure fairness
            p1_is_agent1 = (i % 2 == 0)
            
            if p1_is_agent1:
                env.run([agent1, agent2])
            else:
                env.run([agent2, agent1])
                
            final_step = env.steps[-1]
            
            # Check for errors in the final status
            if final_step[0].status == "ERROR" or final_step[1].status == "ERROR":
                results["errors"] += 1
                print(f"Game {i+1} ended in ERROR.")
                continue

            reward_0 = final_step[0].reward or 0
            reward_1 = final_step[1].reward or 0

            if p1_is_agent1:
                r_a1, r_a2 = reward_0, reward_1
            else:
                r_a1, r_a2 = reward_1, reward_0

            results["a1_rewards"].append(r_a1)
            results["a2_rewards"].append(r_a2)

            if r_a1 > r_a2:
                results["wins_a1"] += 1
                winner = args.agent
            elif r_a2 > r_a1:
                results["wins_a2"] += 1
                winner = args.opponent
            else:
                results["ties"] += 1
                winner = "Tie"

            game_log = {
                "game": i + 1,
                "seed": seed,
                "a1_reward": r_a1,
                "a2_reward": r_a2,
                "winner": winner,
                "p1_is_a1": p1_is_agent1
            }
            results["game_logs"].append(game_log)
            print(f"Game {i+1}/{args.games} (Seed {seed}): {args.agent} ${r_a1} vs {args.opponent} ${r_a2} -> Winner: {winner}")
            
        except Exception as e:
            results["errors"] += 1
            print(f"Game {i+1} failed with error: {e}")
            
    print("\n--- Final Statistics ---")
    print(f"Total Games: {args.games}")
    valid_games = len(results["a1_rewards"])
    
    if valid_games > 0:
        print(f"{args.agent} Wins: {results['wins_a1']} ({results['wins_a1']/valid_games*100:.1f}%)")
        print(f"{args.opponent} Wins: {results['wins_a2']} ({results['wins_a2']/valid_games*100:.1f}%)")
        print(f"Ties: {results['ties']}")
        print(f"Errors/Crashes: {results['errors']}")
        
        a1_arr = np.array(results["a1_rewards"])
        a2_arr = np.array(results["a2_rewards"])
        
        stats_a1 = {
            "mean": float(np.mean(a1_arr)),
            "median": float(np.median(a1_arr)),
            "std": float(np.std(a1_arr)),
            "min": float(np.min(a1_arr)),
            "max": float(np.max(a1_arr))
        }
        
        stats_a2 = {
            "mean": float(np.mean(a2_arr)),
            "median": float(np.median(a2_arr)),
            "std": float(np.std(a2_arr)),
            "min": float(np.min(a2_arr)),
            "max": float(np.max(a2_arr))
        }
        
        results["stats_a1"] = stats_a1
        results["stats_a2"] = stats_a2
        
        print(f"\n{args.agent} Performance:")
        print(f"  Mean:   ${stats_a1['mean']:.2f}")
        print(f"  Median: ${stats_a1['median']:.2f}")
        print(f"  StdDev: ${stats_a1['std']:.2f}")
        print(f"  Min:    ${stats_a1['min']:.2f}")
        print(f"  Max:    ${stats_a1['max']:.2f}")
        
        print(f"\n{args.opponent} Performance:")
        print(f"  Mean:   ${stats_a2['mean']:.2f}")
        print(f"  Median: ${stats_a2['median']:.2f}")
        print(f"  StdDev: ${stats_a2['std']:.2f}")
        print(f"  Min:    ${stats_a2['min']:.2f}")
        print(f"  Max:    ${stats_a2['max']:.2f}")
    else:
        print("No valid games completed.")

    # Save to JSON
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {args.output}")
    
    # Save to Markdown Scorecard
    md_output = args.output.replace(".json", ".md")
    with open(md_output, "w") as f:
        f.write(f"# Benchmark Scorecard\n\n")
        f.write(f"| Agent | Opponent | Games | Win % | Avg Bank | Median | Std | Min | Max |\n")
        f.write(f"| ----- | -------- | ----: | ----: | -------: | -----: | --: | --: | --: |\n")
        if valid_games > 0:
            win_pct1 = results['wins_a1']/valid_games*100
            f.write(f"| {args.agent} | {args.opponent} | {valid_games} | {win_pct1:.1f}% | ${stats_a1['mean']:.2f} | ${stats_a1['median']:.2f} | ${stats_a1['std']:.2f} | ${stats_a1['min']:.2f} | ${stats_a1['max']:.2f} |\n")
            win_pct2 = results['wins_a2']/valid_games*100
            f.write(f"| {args.opponent} | {args.agent} | {valid_games} | {win_pct2:.1f}% | ${stats_a2['mean']:.2f} | ${stats_a2['median']:.2f} | ${stats_a2['std']:.2f} | ${stats_a2['min']:.2f} | ${stats_a2['max']:.2f} |\n")
    print(f"Scorecard saved to {md_output}")

if __name__ == "__main__":
    main()
