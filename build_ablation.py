import os
import re

def build_ablated_v104():
    with open('submission_v104_quote_priority.py', 'r', encoding='utf-8') as f:
        src = f.read()
    
    # We want to replace the V93 override with just setting it to the default route, or just removing the override logic entirely.
    # The safest way is to replace the `if` condition with `if False:`
    
    router_regex = r"if 'YARN_STORE' in shops and state\.get\('rkey'\) in _V93_ROUTE_BY_RIVAL:"
    new_src = re.sub(router_regex, r"if False:", src, flags=re.DOTALL)
    
    # Let's also verify it replaced something
    if new_src == src:
        print("Failed to replace CTRTABLE trigger")
        return
        
    out_path = 'agents/v119_ablate_ctrtable.py'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(new_src)
            
    print(f"Generated {out_path}.")

if __name__ == '__main__':
    build_ablated_v104()
