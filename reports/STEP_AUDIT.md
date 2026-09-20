# Step Accessor Audit

## Current Environment Behavior
A rigorous test (`tests/test_step_consistency.py`) was conducted against the currently installed `kaggle_environments` engine (via `make("kaggriculture")`).
- **Seat 0:** Receives `obs["step"]` starting at 0, incrementing by 1 per turn.
- **Seat 1:** Receives `obs["step"]` starting at 0, incrementing by 1 per turn.

**Conclusion:** The environment behaves completely symmetrically. There is **no turn-0 repetition bug** and no shifted step offset for Seat 1 in the current installed version of the simulator. Any agent code employing offsets, look-behind patches, or turn-0 skips for `player == 1` is working around a bug that no longer exists (or never existed locally and only existed on Kaggle backend in an older version).

## Canonical Time Accessor Recommendation
To ensure maximum safety against potential engine reversion while utilizing the correct day/hour semantics (since some agents rely heavily on day arithmetic), all agents should adopt the following canonical time accessor:

```python
raw_step = obs.get("step")
if raw_step is not None:
    step = int(raw_step)
else:
    # Fallback if step is ever stripped from the observation space
    step = int(obs.get("day", 0)) * 24 + int(obs.get("hour", 0))
```

This accessor is robust against Kaggle environment updates and ensures accurate progression tracking without assuming buggy seat offsets.
