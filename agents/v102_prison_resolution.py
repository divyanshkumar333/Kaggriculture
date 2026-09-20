import sys, importlib.util
sys.path.insert(0, '.')
spec = importlib.util.spec_from_file_location('m', 'main.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def _future_target_patched(step, item, state):
    opp_shed = state.get('opp_shed', {})
    opp_qty = opp_shed.get(item, 0)
    if opp_qty >= 2:
        return (step + 1, opp_qty)
    max_lookahead = 5
    for offset in range(1, max_lookahead + 1):
        fut = step + offset
        if 0 <= fut < len(mod._ACTIONS):
            q = sum((max(0, int(order[2])) for order in mod._ACTIONS[fut].get('market') or [] if len(order) >= 3 and order[0] == 'SELL' and (order[1] == item)))
            if q > 0:
                return (fut, q)
    return (None, 0)

def agent(obs, cfg=None):
    original = mod._future_target
    mod._future_target = _future_target_patched
    try:
        action = mod.agent(obs, cfg)
    finally:
        mod._future_target = original
    return action
