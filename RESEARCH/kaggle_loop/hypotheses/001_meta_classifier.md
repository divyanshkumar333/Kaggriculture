# Hypothesis 001: Opponent Meta Classifier

**Date**: September 17, 2026

## Research Direction
**Direction C**: Opponent Meta Classifier.

## Motivation
Recent submissions (V057 to V069) have relied on single, fixed macroeconomic plans (like Melon frontrunning or pure Strawberry) or simple heuristic adaptations (depth search for market spoilers). However, the Kaggle environment has a shared market. A fixed macro plan that overlaps with the opponent's plan results in market cannibalization (e.g., both players crashing the Melon or Milk price). 

## Hypothesis
If an agent observes the opponent's purchases and plantings during the first 2-3 days (48-72 steps) to classify their strategy (Melon-heavy vs Livestock-heavy vs Strawberry-heavy), and dynamically switches to an orthogonal counter-strategy (e.g., dodging Melons if the opponent goes Melons, or exploiting Strawberries if the opponent ignores them), then the agent will achieve a higher head-to-head win rate than a monolithic fixed-tape strategy because it avoids market cannibalization.

## Implementation Plan (Meta-Classifier Agent)
1. **Feature Extraction**: Monitor opponent's shed inventory and market purchases (inferred via market deltas or direct tile observation) during Day 0 to Day 3.
2. **Classification Rules**:
   - `MELON_RUSH`: Opponent plants > 8 Melons or buys > 8 Melon seeds.
   - `LIVESTOCK_RUSH`: Opponent buys >= 2 Cows/Sheep early.
   - `PASSIVE/WEAK`: Opponent does very little.
3. **Counter-Policy Selection**:
   - If `MELON_RUSH`: Switch to a Strawberry/Livestock tape that completely ignores Melons to avoid the Day 6-8 price crash.
   - If `LIVESTOCK_RUSH`: Switch to a heavy Melon + Strawberry tape, since Milk/Wool prices will be depressed.
   - Default: Play the optimal balanced (V060/V027-style) tape.
4. **Architecture**:
   The agent will carry 2-3 compressed JSON replays (tapes) inside its code. At step 0, it follows the Default tape. At step 72 (Day 3 start), it permanently selects the optimal tape based on the opponent's board state.

## Prediction
This agent will dominate mirror matches against pure Melon or pure Livestock agents by capturing the uncontested market segment, resulting in a higher win probability across a diverse opponent pool and thus a higher Kaggle rating.
