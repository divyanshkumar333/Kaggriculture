import json
import zlib
import base64
import ast
import collections

def analyze_tape(tape):
    # tape is a list of 720 dictionaries. Each dict may have 'market', 'farmer', 'hands' etc.
    stats = collections.defaultdict(int)
    
    for step in tape:
        if 'market' in step:
            for m in step['market']:
                if not m: continue
                if m[0] == 'SELL':
                    stats[m[1]] += m[2]
                elif m[0] == 'BUY_SEED':
                    stats['buy_seed_' + m[1]] += m[2]
                elif m[0] == 'HIRE':
                    stats['hires'] += 1
                elif m[0] == 'BUY_ANIMAL':
                    stats['buy_animal_' + m[1]] += m[2]
    return dict(stats)

def main():
    with open('submission_v104_quote_priority.py', 'r', encoding='utf-8') as f:
        src = f.read()
    
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '_R108_DATA':
                    b85_str = node.value.args[0].args[0].args[0].value
                    data = json.loads(zlib.decompress(base64.b85decode(b85_str)).decode('utf-8'))
                    
                    routes = data['routes']
                    actions = data['actions']
                    
                    results = {}
                    for r_id, action_ids in routes.items():
                        tape = [actions[i] for i in action_ids]
                        stats = analyze_tape(tape)
                        results[r_id] = stats
                        
                    with open('route_static_analysis.json', 'w') as out:
                        json.dump(results, out, indent=2)
                    print("Static analysis complete. Wrote to route_static_analysis.json")
                    return

if __name__ == '__main__':
    main()
