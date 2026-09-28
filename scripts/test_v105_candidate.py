import subprocess

agent_file = 'agents/v117_demand_residual.py'
opponents = ['agents/v116_carrot_margin_optimized.py']
seeds = [42, 101, 202, 303, 404]

for opp in opponents:
    wins = 0
    ties = 0
    losses = 0
    print(f'--- vs {opp} ---')
    for s in seeds:
        script = f'''from kaggle_environments import make
import json
env = make("kaggriculture", configuration={{"episodeSteps": 720, "randomSeed": {s}}})
final = env.run(["{agent_file}", "{opp}"])[-1]
m1 = final[0].observation.farms[0]["money"]
m2 = final[1].observation.farms[1]["money"]
print(f"RESULT:{{m1}},{{m2}}")
'''
        with open('temp_run_2.py', 'w') as f:
            f.write(script)
        
        res = subprocess.run(['.\\.venv\\Scripts\\python', 'temp_run_2.py'], capture_output=True, text=True)
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
            print(f'Seed {s} error: {e}')

    print(f'Result vs {opp}: {wins} W / {ties} T / {losses} L\n')
