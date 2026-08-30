from kaggle_environments import make
import importlib.util

def load_agent(filepath):
    if filepath in ["random", "pass", "starter"]:
        return filepath
    spec = importlib.util.spec_from_file_location(f"agent_{abs(hash(filepath))}", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "agent")

def test_fresh_suite():
    agent_c = load_agent("agents/v020_c_competitive_surgical.py")
    agent_a = load_agent("agents/v020_a_control.py")
    
    seeds = [300, 301, 302, 303, 304, 305, 306, 307, 308, 309]
    
    print("==================================================")
    print("FRESH SEEDS H2H: V020-C vs V020-A Control (10 seeds, alternating)")
    print("==================================================")
    
    c_wins = 0
    a_wins = 0
    c_banks = []
    a_banks = []
    
    for i, s in enumerate(seeds):
        p0_is_c = (i % 2 == 0)
        agents = [agent_c, agent_a] if p0_is_c else [agent_a, agent_c]
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": s}, debug=True)
        env.run(agents)
        
        c_idx = 0 if p0_is_c else 1
        a_idx = 1 if p0_is_c else 0
        
        rc = float(env.steps[-1][c_idx].reward or 0)
        ra = float(env.steps[-1][a_idx].reward or 0)
        c_banks.append(rc)
        a_banks.append(ra)
        
        if rc > ra:
            c_wins += 1
            w = "V020-C"
        elif ra > rc:
            a_wins += 1
            w = "V020-A Control"
        else:
            w = "TIE"
            
        pos = "P0" if p0_is_c else "P1"
        print(f"Seed {s:3d} | V020-C ({pos}): ${rc:6.0f} | V020-A: ${ra:6.0f} | Delta: ${rc-ra:+6.0f} | Winner: {w}")

    print(f"\nScore: V020-C {c_wins}W - {a_wins}L | Mean C: ${sum(c_banks)/len(c_banks):.0f} | Mean A: ${sum(a_banks)/len(a_banks):.0f}")

if __name__ == "__main__":
    test_fresh_suite()
