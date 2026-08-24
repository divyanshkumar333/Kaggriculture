import json
from collections import defaultdict
from kaggle_environments import make

def run_agent_game(agent_file, opponent="random", seed=42):
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed})
    # Run the game
    env.run([agent_file, opponent])
    
    # Analyze the result
    final_step = env.steps[-1]
    # Agent is player 0
    reward = final_step[0].reward
    
    # We want to extract metrics from the agent's stderr/stdout or we can just run the analyze_v009 logic.
    # To get metrics without external parser, we can capture the final state.
    # However, since the agent prints metrics to stdout at the end, we can parse env.logs or standard output.
    return reward

def main():
    import sys
    import subprocess
    import ast
    
    # We will use the analyze_v009.py logic which is already built!
    # Wait, analyze_v009.py runs 1 game by default, or multiple if we pass args.
    # Let's just use subprocess to run analyze_v009.py twice.
    
    print("Running V009-A Smoke Test...")
    res_a = subprocess.run([
        sys.executable, "analyze_v009.py", 
        "--agent", "agents/v009_a_control.py", 
        "--games", "5"
    ], capture_output=True, text=True)
    print("V009-A Completed.")
    
    print("Running V009-B Smoke Test...")
    res_b = subprocess.run([
        sys.executable, "analyze_v009.py", 
        "--agent", "agents/v009_b_harvest_timing.py", 
        "--games", "5"
    ], capture_output=True, text=True)
    print("V009-B Completed.")
    
    with open("v009_smoke_test_report.md", "w") as f:
        f.write("# V009 Smoke Test Report\n\n")
        f.write("## V009-A (Control)\n```\n")
        f.write(res_a.stdout)
        f.write("```\n\n")
        f.write("## V009-B (Harvest Timing Fix)\n```\n")
        f.write(res_b.stdout)
        f.write("```\n")
        
    print("Report written to v009_smoke_test_report.md")

if __name__ == '__main__':
    main()
