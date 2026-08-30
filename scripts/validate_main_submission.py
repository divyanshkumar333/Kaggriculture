from kaggle_environments import make
import importlib.util

def load_agent(filepath):
    if filepath in ["random", "pass", "starter"]:
        return filepath
    spec = importlib.util.spec_from_file_location("main_submission", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "agent")

def test_submission():
    print("==================================================")
    print("RUNNING FINAL LOCAL SUBMISSION VALIDATION FOR main.py")
    print("==================================================")
    
    agent_fn = load_agent("main.py")
    
    # 1. Test vs random (P0 and P1)
    for p0_is_main in [True, False]:
        pos_str = "P0 (First)" if p0_is_main else "P1 (Second)"
        print(f"\nTesting main.py as {pos_str} vs random...")
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
        agents = [agent_fn, "random"] if p0_is_main else ["random", agent_fn]
        env.run(agents)
        final = env.steps[-1]
        
        main_idx = 0 if p0_is_main else 1
        opp_idx = 1 if p0_is_main else 0
        
        main_reward = float(final[main_idx].reward or 0)
        opp_reward = float(final[opp_idx].reward or 0)
        main_status = final[main_idx].status
        
        print(f"  -> Status: {main_status} | Main Reward: ${main_reward:,.0f} | Opp Reward: ${opp_reward:,.0f}")
        assert main_status == "DONE", f"Main status is {main_status}, expected DONE"
        assert main_reward > opp_reward, f"Main reward ${main_reward} did not beat opponent ${opp_reward}"
        
    # 2. Test vs starter (P0 and P1)
    for p0_is_main in [True, False]:
        pos_str = "P0 (First)" if p0_is_main else "P1 (Second)"
        print(f"\nTesting main.py as {pos_str} vs starter...")
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 100}, debug=True)
        agents = [agent_fn, "starter"] if p0_is_main else ["starter", agent_fn]
        env.run(agents)
        final = env.steps[-1]
        
        main_idx = 0 if p0_is_main else 1
        opp_idx = 1 if p0_is_main else 0
        
        main_reward = float(final[main_idx].reward or 0)
        opp_reward = float(final[opp_idx].reward or 0)
        main_status = final[main_idx].status
        
        print(f"  -> Status: {main_status} | Main Reward: ${main_reward:,.0f} | Opp Reward: ${opp_reward:,.0f}")
        assert main_status == "DONE", f"Main status is {main_status}, expected DONE"
        assert main_reward > opp_reward, f"Main reward ${main_reward} did not beat opponent ${opp_reward}"

    print("\n==================================================")
    print("ALL STANDALONE TESTS PASSED (0 ERRORS, 0 CRASHES, 100% WIN RATE)")
    print("==================================================")

if __name__ == "__main__":
    test_submission()
