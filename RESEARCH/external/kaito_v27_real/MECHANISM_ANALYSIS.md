# Kaito v27 Mechanism Analysis

## Overview
This document analyzes the actual `main.py` extracted from the public Kaggle artifact `kaitofukami/25-27-strict-future-v27-midgame-meta-reset`.

## The "Strict-Future" Revelation
Contrary to the hypothesis that Kaito used a "Strict-Future constraint" to dynamically infer opponent state for front-running, **Kaito v27 contains zero front-running logic**. 
- There is no `_front_run` function.
- There is no `_future_target` lookahead.
- There is no opponent-shed inference.

Kaito strictly relies on executing the encoded trace (`_LEGACY_ACTIONS`), and only dynamically overrides the market sell ordering and weed repair. It literally removes the future lookahead by simply not having one.

## The "Midgame Meta Reset" Myth
The agent name implies a mid-game evaluation of the route. However, the code contains no turn-based structural branching (no `step == 360` logic). 
Instead, the "reset" or "branching" is completely contained in the `_regime` detection at turn 0:
```python
def _regime(configuration):
    interval = int(_get(configuration, "townCenterSellInterval", 12) or 12)
    return "rebalance" if interval >= 24 else "legacy"
```
While `_REBALANCE_ACTIONS` is assigned to `_LEGACY_ACTIONS` in this specific file, the logic scales demand differently based on the regime.

## Dynamic Order Scoring (`_order_score`)
Instead of just price impact, Kaito adjusts the value of a sell slot based on the Town's demand rate.
```python
demand = max(0.25, _demand_per_day(obs, configuration, item))
excess = max(0.0, current_inventory + quantity - 10000)
urgency = min(1.0, (excess / demand) / 10.0)
return score * (1.0 + _DEMAND_ALPHA * urgency)
```
This forces the agent to sell items that are in high excess relative to the town's consumption rate, avoiding market crashes.

## Conclusion
Kaito v27 scores 3090.1 not by building complex opponent models or meta-resets, but by **simplifying**. It deleted the brittle front-running logic that V057 uses, relying entirely on demand-weighted market sorting and weed repair, proving that V057's lookahead is actively harmful.
