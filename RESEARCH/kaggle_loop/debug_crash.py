import json
import traceback
import sys

sys.path.append("experiments/meta_classifier")
import main

def debug():
    with open("episode-110091442-replay.json") as f:
        data = json.load(f)
        
    for step_idx, step in enumerate(data["steps"]):
        # Test player 0
        obs0 = step[0].get("observation", {})
        if not obs0: obs0 = step[0]
        if isinstance(obs0, str):
            try: obs0 = json.loads(obs0)
            except: pass
            
        try:
            main.agent(obs0)
        except Exception as e:
            print(f"P0 Error at step {step_idx}:")
            traceback.print_exc()
            break
            
        # Test player 1
        if len(step) > 1:
            obs1 = step[1].get("observation", {})
            if not obs1: obs1 = step[1]
            if isinstance(obs1, str):
                try: obs1 = json.loads(obs1)
                except: pass
                
            try:
                main.agent(obs1)
            except Exception as e:
                print(f"P1 Error at step {step_idx}:")
                traceback.print_exc()
                break

if __name__ == "__main__":
    debug()
