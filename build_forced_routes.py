import os
import re

def build_forced_agents():
    with open('submission_v104_quote_priority.py', 'r', encoding='utf-8') as f:
        src = f.read()
    
    # We want to replace the _router function. 
    # Let's find its start and end.
    # The router looks like:
    # def _router(observation,step,state):
    #     if step==2:
    #        ...
    #     return state.get('route',0)
    
    router_regex = r"def _router\(observation,step,state\):.*?return state\.get\('route',0\)"
    
    routes = list(range(13)) + list(range(100, 129))
    
    os.makedirs('agents/forced_routes', exist_ok=True)
    
    for r in routes:
        replacement = f"def _router(observation,step,state):\n    return {r}"
        new_src = re.sub(router_regex, replacement, src, flags=re.DOTALL)
        
        with open(f'agents/forced_routes/v104_route_{r}.py', 'w', encoding='utf-8') as f:
            f.write(new_src)
            
    print(f"Generated {len(routes)} forced route agents.")

if __name__ == '__main__':
    build_forced_agents()
