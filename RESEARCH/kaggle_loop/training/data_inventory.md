# Replay Data Inventory

**Generated**: September 17, 2026

## Available Local Replays
The following replay types were identified in the local repository:

- `episode-*-replay.json` (8 episodes)
- Total valid Kaggriculture episodes: 8
- Total timesteps available for training: 5,760 (720 steps per episode)

### Kaggriculture Engine Context
- Engine Version: Kaggle `kaggriculture` (episodes downloaded via CLI).
- Available Observation State:
  - `step`, `day`, `hour`
  - `player`
  - `farms` (includes `money`, `tiles`, `farmer`, `hands`, `unlocked_quadrants`)
  - `private` (includes `shed`, `seeds`, `inventories` for the active player only, or both if parsed from global state)
  - `market` (includes `inventory`, `prices`)
  - `town` (`unlocked_shops`)
- Available Actions (per step):
  - `farmer`: `[action, *args]`
  - `hands`: `[[action, *args], ...]`
  - `market`: `[[action, *args], ...]`
- Final Rewards:
  - Represented as final cash at step 720.
  - Winner and loser labels can be deterministically extracted from the final step's `reward` property.

### Limitations & Leakage Prevention
- **State Masking**: Replay files often contain global state (the full `farms` object for both players, including their private seeds/shed). For training, we must strictly mask the opponent's `private` fields and only use observable board state (e.g., inferring shed quantities based on observed harvests and market actions) to prevent information leakage.
- **Data Volume**: 8 episodes (5,760 states) is enough to prototype the ML pipeline (dataset builder, features, simple XGBoost/Logistic Regression classifiers), but we will need more Kaggle replays to capture the diversity of the 2800+ rating meta.
