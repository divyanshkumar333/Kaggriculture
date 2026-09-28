from kaggle_environments import make
import json
env = make("kaggriculture", configuration={"episodeSteps": 720, "randomSeed": 404})
final = env.run(["agents/v115_margin_30.py", "agents/v104_quote_priority.py"])[-1]
m1 = final[0].observation.farms[0]["money"]
m2 = final[1].observation.farms[1]["money"]
print(f"RESULT:{m1},{m2}")
