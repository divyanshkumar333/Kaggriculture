import traceback
from kaggle_environments import make

def main():
    env = make('kaggriculture', debug=True)
    try:
        env.run(['agents/v057_deep_frontrun.py', 'agents/v060_melon_frontrunner.py'])
        print(env.steps[-1][0].reward, env.steps[-1][1].reward)
    except Exception as e:
        traceback.print_exc()
        
    for step in env.steps:
        if step[0].status == 'ERROR':
            print("P0 ERROR!")
        if step[1].status == 'ERROR':
            print("P1 ERROR!")
            
if __name__ == "__main__":
    main()
