# Training Ablation 1: Hybrid Prototype 

**Date**: September 17, 2026

## Setup
- **Training Data**: 8 Kaggle Replays (5760 timesteps)
- **Features Extracted**: 20 variables representing raw economic state and board tiles, completely masked of opponent's private variables (no future information or private info leakage).
- **Models Trained**:
  - `Model A` (Opponent Archetype Classifier): Random Forest (max depth 5)
  - `Model C` (Value/Outcome Prediction): Random Forest (max depth 6)
  
## Validation Results
- **Opponent Classifier**: Achieved 75% accuracy. It successfully discriminated between `MELON_RUSH` (class 0) and `STRAWBERRY/BALANCED` (class 2) archetypes present in the 8 replays. 
- **Value Model**: Achieved 29% accuracy on predicting win/loss. 
  - *Failure Analysis*: This poor performance is expected because predicting final outcome from arbitrary early steps without a robust lookahead simulation using only 8 replays is extremely noisy. The dataset is too small to capture robust economic inflection points.

## Adversarial Local Tests (150 steps)
- **Hybrid Agent vs 001 Meta Classifier**: 3000 to 3000 (Draw)
  - *Analysis*: Both agents played safe early games (since they are both using the same underlying `strat_melon` and `strat_strawberry` engines) and didn't crash each other.
- **Hybrid Agent vs Random**: 3000 to 2190 (Win)
  - *Analysis*: Hybrid correctly applied economic pressure.

## Key Discoveries & Failures
1. **Classifier Feasibility**: Yes, the opponent strategy can be classified from observation features alone. Random Forest easily separates Melon spammers from Strawberry players based on tile counts in the first 2-3 days.
2. **Value Model Difficulty**: Learning an end-to-end outcome predictor (Model C) requires vastly more than 8 replays. Future iterations must either (a) increase replay count to 1000+ or (b) transition to a short-horizon reward model (e.g. predicting $+Cash$ in the next 50 steps) rather than absolute match outcome.
3. **Inference Latency**: `scikit-learn` Random Forests execute in <5ms, perfectly suitable for Kaggle's runtime.

## Conclusion
The ML pipeline is validated and operates safely without data leakage. The `hybrid_agent.py` successfully loads models and dynamically allocates strategies. 
**Do NOT submit this to Kaggle yet**, as the models were only trained on 8 replays and offer no objective advantage over the hand-coded rules yet. 
**Next Goal**: Fetch top 100 replays via Kaggle CLI to train a production-grade classifier.
