import subprocess
import os

margins = [-10.0, -15.0, -20.0, -25.0, -30.0]
seeds = [42, 101, 202, 303, 404]

for m in margins:
    with open('agents/v104_quote_priority.py', 'r') as f:
        code = f.read()
    code = code.replace('_CA_MARGIN = -5.0', f'_CA_MARGIN = {m}')
    agent_file = f'agents/v115_margin_{int(abs(m))}.py'
    with open(agent_file, 'w') as f:
        f.write(code)

    wins = 0
    ties = 0
    losses = 0
    print(f'--- Margin {m} ---')
    for s in seeds:
        script = f'''from kaggle_environments import make
import json
env = make("kaggriculture", configuration={{"episodeSteps": 720, "randomSeed": {s}}})
final = env.run(["{agent_file}", "agents/v104_quote_priority.py"])[-1]
m1 = final[0].observation.farms[0]["money"]
m2 = final[1].observation.farms[1]["money"]
print(f"RESULT:{{m1}},{{m2}}")
'''
        with open('temp_run.py', 'w') as f:
            f.write(script)
        
        res = subprocess.run(['.\\.venv\\Scripts\\python', 'temp_run.py'], capture_output=True, text=True)
        try:
            output = [line for line in res.stdout.split('\n') if line.startswith('RESULT:')][-1]
            m1, m2 = map(float, output.replace('RESULT:', '').strip().split(','))
            if m1 > m2:
                wins += 1
                print(f'Seed {s}: W ({m1} > {m2})')
            elif m2 > m1:
                losses += 1
                print(f'Seed {s}: L ({m1} < {m2})')
            else:
                ties += 1
                print(f'Seed {s}: T ({m1} == {m2})')
        except Exception as e:
            print(f'Seed {s} error: {e}, stdout: {res.stdout}, stderr: {res.stderr}')

    print(f'Margin {m}: {wins} W / {ties} T / {losses} L\n')
