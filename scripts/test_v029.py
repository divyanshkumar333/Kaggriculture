from kaggle_environments import make
import importlib.util
import time

def load_agent(filepath):
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "agent")

def test_fresh_suite():
    agent_new = load_agent("agents/v029_hybrid_frontrun.py")
    agent_v16 = load_agent("agents/public_v16_rc5.py")
    
    seeds = [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]
    
    print("==================================================")
    print("FRESH SEEDS H2H: V029 vs V16-RC5 (20 seeds, alternating)")
    print("==================================================")
    
    new_wins = 0
    v16_wins = 0
    new_banks = []
    v16_banks = []
    
    for i, s in enumerate(seeds):
        p0_is_new = (i % 2 == 0)
        agents = [agent_new, agent_v16] if p0_is_new else [agent_v16, agent_new]
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s})
        env.run(agents)
        
        c_idx = 0 if p0_is_new else 1
        a_idx = 1 if p0_is_new else 0
        
        # Check for errors
        failed = False
        for status in env.steps[-1]:
            if status.status in ["ERROR", "TIMEOUT", "INVALID"]:
                failed = True
                
        if failed:
            print(f"Seed {s} FAILED with status {[s.status for s in env.steps[-1]]}")
            continue
            
        rc = float(env.steps[-1][c_idx].reward or 0)
        ra = float(env.steps[-1][a_idx].reward or 0)
        new_banks.append(rc)
        v16_banks.append(ra)
        
        if rc > ra:
            new_wins += 1
            w = "V029"
        elif ra > rc:
            v16_wins += 1
            w = "V16-RC5"
        else:
            w = "TIE"
            
        pos = "P0" if p0_is_new else "P1"
        print(f"Seed {s:3d} | V029 ({pos}): ${rc:6.0f} | V16: ${ra:6.0f} | Delta: ${rc-ra:+6.0f} | Winner: {w}")

    print(f"\nScore: V029 {new_wins}W - {v16_wins}L | Mean V029: ${sum(new_banks)/len(new_banks):.0f} | Mean V16: ${sum(v16_banks)/len(v16_banks):.0f}")

if __name__ == "__main__":
    start = time.time()
    test_fresh_suite()
    print(f"Completed in {time.time()-start:.1f}s")
