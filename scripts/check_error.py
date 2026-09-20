import json
import sys

def main(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    steps = data.get('steps', [])
    print(f"Total steps: {len(steps)}")
    final = steps[-1]
    print(f"P0 Status: {final[0]['status']}")
    print(f"P1 Status: {final[1]['status']}")
    
    for i, step in enumerate(steps):
        if step[1]['status'] == 'ERROR':
            print(f"P1 ERROR at step {i}")
            break
            
if __name__ == '__main__':
    main(sys.argv[1])
