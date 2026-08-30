from kaggle_environments import make
import importlib.util
import os

def load_agent(filepath):
    if filepath in ["random", "pass", "starter"]:
        return filepath
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "agent")

def run_smoke():
    print("==================================================")
    print("RUNNING 5-GAME SMOKE TEST FOR V020-C")
    print("==================================================")
    
    agent_c = load_agent("agents/v020_c_competitive_surgical.py")
    agent_a = load_agent("agents/v020_a_control.py")
    
    opponents = [
        ("Random (P1)", "random", True),
        ("Random (P0)", "random", False),
        ("Starter (P1)", "starter", True),
        ("Starter (P0)", "starter", False),
        ("V020-A Control", agent_a, True)
    ]
    
    for i, (name, opp, p0_is_c) in enumerate(opponents):
        seed = 42 + i
        agents = [agent_c, opp] if p0_is_c else [opp, agent_c]
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
        env.run(agents)
        
        c_idx = 0 if p0_is_c else 1
        opp_idx = 1 if p0_is_c else 0
        
        final = env.steps[-1]
        c_reward = float(final[c_idx].reward or 0)
        opp_reward = float(final[opp_idx].reward or 0)
        status = final[c_idx].status
        
        print(f"Game {i+1} vs {name:<16} (Seed {seed}) | Status: {status} | V020-C: ${c_reward:6.0f} | Opp: ${opp_reward:6.0f} | Winner: {'V020-C' if c_reward > opp_reward else 'Opponent'}")
        assert status == "DONE", f"Game failed with status {status}"

    print("\n==================================================")
    print("ALL 5 SMOKE TESTS PASSED CLEANLY (0 ERRORS, 0 CRASHES)")
    print("==================================================")

if __name__ == "__main__":
    run_smoke()
