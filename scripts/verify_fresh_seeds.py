from kaggle_environments import make
import importlib.util

def load_agent(filepath):
    if filepath in ["random", "pass", "starter"]:
        return filepath
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "agent")

def run_fresh_verification():
    print("==================================================")
    print("RUNNING FRESH VALIDATION ON UNSEEN SEEDS (300-304)")
    print("==================================================")
    
    agent_c = load_agent("agents/v020_c_competitive_surgical.py")
    agent_a = load_agent("agents/v020_a_control.py")
    
    test_cases = [
        ("Random (P1)", "random", True, 300),
        ("Starter (P1)", "starter", True, 301),
        ("V020-A Control (P1)", agent_a, True, 302),
        ("V020-A Control (P0)", agent_a, False, 303),
        ("Starter (P0)", "starter", False, 304)
    ]
    
    for name, opp, p0_is_c, seed in test_cases:
        agents = [agent_c, opp] if p0_is_c else [opp, agent_c]
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=True)
        env.run(agents)
        
        c_idx = 0 if p0_is_c else 1
        opp_idx = 1 if p0_is_c else 0
        
        final = env.steps[-1]
        c_reward = float(final[c_idx].reward or 0)
        opp_reward = float(final[opp_idx].reward or 0)
        status = final[c_idx].status
        
        print(f"Seed {seed:3d} vs {name:<20} | Status: {status} | V020-C: ${c_reward:6.0f} | Opp: ${opp_reward:6.0f} | Winner: {'V020-C' if c_reward > opp_reward else 'Opponent'}")
        assert status == "DONE", f"Game failed with status {status}"
        assert c_reward > opp_reward, f"V020-C (${c_reward}) did not beat {name} (${opp_reward})"

    print("\n==================================================")
    print("ALL FRESH SEED TESTS PASSED (100% WIN RATE, 0 CRASHES)")
    print("==================================================")

if __name__ == "__main__":
    run_fresh_verification()
