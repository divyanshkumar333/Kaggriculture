"""
Test what happens if we force V104 to use Route 1 (High Output) even without YARN_STORE.
"""
import sys, importlib.util
sys.path.insert(0, r'e:\Setup\kaggle\kaggriculture')
from kaggle_environments import make

spec = importlib.util.spec_from_file_location("v104", r"e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py")
v104 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v104)

# Monkey patch v104 router to always return route 1
original_router = v104._router
def forced_router(obs, state, routes):
    original_router(obs, state, routes)
    state['route'] = 1
    return 1

v104._IMPL.chassis.router = forced_router
v104._router = forced_router

env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 101}, debug=True)
env.run([v104.agent, "pass"])

final_state = env.steps[-1][0]['observation']
player_money = final_state['farms'][0]['money']
print(f"Final money for Forced Route 1 (No Yarn Store): {player_money}")
