import sys
import os
from kaggle_environments import make

agents = [
    'agents/ablations/v104_minus_b_quote_priority.py',
    'agents/ablations/v104_minus_c_care_gating.py',
    'agents/ablations/v104_minus_d_ctrtable.py',
    'agents/ablations/v104_minus_e_terminal.py',
]

for a in agents:
    print(f"Testing {a}...")
    try:
        env = make("kaggriculture", configuration={"episodeSteps": 10}, debug=True)
        env.run([a, "random"])
        print("Success.")
    except Exception as e:
        print(f"FAILED: {e}")
