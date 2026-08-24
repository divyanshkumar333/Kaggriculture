import sys
import subprocess

agent = "agents/v017_b_depreciated_pipeline.py"
opp = "random"
cmd = [
    sys.executable, "-c",
    f"import os; os.environ['KAGGRICULTURE_SEED'] = '0'; from kaggle_environments import make; env = make('kaggriculture', configuration={{'episodeSteps': 720}}); env.run(['{agent}', '{opp}']); print('P0 Reward:', env.steps[-1][0].reward); print('P1 Reward:', env.steps[-1][1].reward)"
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:")
print(res.stdout)
print("STDERR:")
print(res.stderr)
