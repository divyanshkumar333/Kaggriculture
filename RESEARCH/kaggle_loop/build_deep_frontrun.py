import re

def main():
    code = open('agents/v057_generalized_spoiler.py').read()
    
    new_fq = """def _future_quantity(step, item):
    qty = 0
    for s in range(step + 1, min(step + 6, len(_ACTIONS))):
        qty += sum(max(0, int(order[2])) for order in (_ACTIONS[s].get("market") or []) if len(order) >= 3 and order[0] == "SELL" and order[1] == item)
    return qty"""

    # We need to replace the old _future_quantity function.
    # The old function looks like this:
    # def _future_quantity(step, item):
    #     future = step + 1
    #     if not 0 <= future < len(_ACTIONS):
    #         return 0
    #     return sum(
    #         max(0, int(order[2]))
    #         for order in (_ACTIONS[future].get("market") or [])
    #         if len(order) >= 3 and order[0] == "SELL" and order[1] == item
    #     )
    
    # We will just find the start of the function, and replace until the next def.
    parts = code.split("def _future_quantity(step, item):")
    before = parts[0]
    after = parts[1].split("def _pickup_reserve(action, item):")[1]
    
    new_code = before + new_fq + "\n\n\ndef _pickup_reserve(action, item):" + after
    
    with open('agents/v057_deep_frontrun.py', 'w') as f:
        f.write(new_code)
        
if __name__ == "__main__":
    main()
