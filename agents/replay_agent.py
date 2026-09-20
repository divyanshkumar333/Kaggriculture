import json
import os
import copy

_ACTIONS = None

def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)

def agent(obs, configuration=None):
    global _ACTIONS
    if _ACTIONS is None:
        trace_path = os.environ.get("REPLAY_AGENT_TRACE")
        if trace_path and os.path.exists(trace_path):
            with open(trace_path) as f:
                _ACTIONS = json.load(f)
        else:
            _ACTIONS = []

    step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
    
    if not _ACTIONS:
        return {"farmer": ["PASS"], "hands": [], "market": []}
        
    action = _ACTIONS[step]
    if action is None:
        action = {}
        
    action = copy.deepcopy(action)
    
    # Align hands
    expected_hands = 0
    farms = _get(obs, "farms", [])
    player = _get(obs, "player", 0)
    if player < len(farms):
        expected_hands = len(_get(farms[player], "hands", []))
    
    hands = list(action.get("hands") or [])
    if len(hands) < expected_hands:
        hands.extend([["PASS"] for _ in range(expected_hands - len(hands))])
    action["hands"] = [list(order or ["PASS"]) for order in hands[:expected_hands]]
    
    if "farmer" not in action or not action["farmer"]:
        action["farmer"] = ["PASS"]
    if "market" not in action or not action["market"]:
        action["market"] = []
        
    return action
