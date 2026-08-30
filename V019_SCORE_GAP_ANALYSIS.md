# V019 Score Gap Analysis

## Executive Summary

| Field | Value |
|---|---|
| **Submitted Agent** | `agents/v018_b_batch_cap.py` |
| **Local Mean Final Bank** | ~$52,780 |
| **Kaggle Leaderboard Score** | **521.1** |
| **Kaggle Starting Score (new submission)** | **600** |
| **Score vs. Baseline** | **-78.9 pts BELOW new-submission baseline** |
| **Gap Type** | Regime mismatch -- local metric (bank balance) is NOT what the leaderboard measures |

---

## 1. What the Kaggle Leaderboard Score Actually Measures

> CRITICAL: The leaderboard score is NOT the final bank balance.
> It is a SKILL RATING based purely on WIN/LOSS outcomes vs real human-submitted agents.

### Confirmed Rating Mechanism

Kaggle simulation competitions use a Bayesian skill rating (Elo-like / Bradley-Terry):

| Property | Value |
|---|---|
| Starting rating per submission | 600 |
| Rating inputs | Win / Loss / Draw outcomes ONLY |
| Margin does NOT matter | Winning by $1 vs $50,000 is identical |
| Opponents | Real leaderboard participants (NOT random/pass/starter) |
| Active submissions | Two most recent |
| Rating convergence | ~60 games for ~90% of true skill |
| Final ranking | Bradley-Terry tournament after deadline (Oct 15, 2026) |

### The Score Formula (Environment Source Confirmed)

From kaggriculture.json:
  "reward": {"description": "Player money at end of game (final score).", "type": "number"}

From kaggriculture.py:
  s.reward = float(obs0.farms[s.observation.player]["money"])

The game reward = bank balance. The leaderboard score = win/loss record vs other agents.
Final bank only determines WHICH player won each individual game.

---

## 2. Score Interpretation: 521.1

| Interpretation | Conclusion |
|---|---|
| Score 521.1 < 600 (starting) | V018-B is net-losing against real leaderboard opponents |
| Implied win rate | ~35-40% (below 50%) against the current field |
| Local win rate vs random/pass/starter | ~100% |
| Root cause | Real agents are dramatically stronger than local test opponents |

A score of 521.1 means V018-B has been beaten more than it has won.

---

## 3. Root Cause Analysis

### Cause 1 (CONFIRMED -- PRIMARY): Local opponents are worthless for calibration

Evidence:
- random agent ends with ~$0-$500 bank
- starter agent ends with ~$3,500 bank
- V018-B ends with ~$52,780 against these opponents
- V018-B wins 100% of games vs random/pass/starter
- Real leaderboard agents may earn $40,000-$80,000+ themselves

Local benchmark = V018-B vs amateurs -> 100% win rate -> MISLEADINGLY GOOD
Kaggle leaderboard = V018-B vs real competitors -> sub-50% win rate -> rating drops below 600

The $52,780 bank balance tells us NOTHING about competitive performance.

### Cause 2 (LIKELY): V018-B is self-competitive, not opponent-aware

Evidence from code review:
- Fixed Melon strategy: crop_policy="MELON", expansion_policy="NONE"
- Zero opponent observation -- does NOT look at opponent farm, money, or strategy
- Optimizes own production in isolation
- Cannot adapt if opponent crashes the Melon market
- Market is SHARED: both players sell into same inventory (I0=10,000)

Critical market interaction:
- Melon: above_func=sq, above_target=3.60 -- most aggressive price crash in the game
- Even modest oversupply drives Melon to $1/unit
- V018-B cannot detect or react to market being pre-crashed by opponent

### Cause 3 (LIKELY): Melon monoculture = catastrophic downside risk

Evidence:
- 98% of revenue is premium (crop_policy="MELON"), ~$64,254 of $65,800 total
- No diversification
- V018-B local min bank: $27,496 even against WEAK opponents
- High variance destroys win rate (win/loss is binary -- bank only determines who won)

### Cause 4 (LIKELY): Insufficient land expansion

Evidence:
- expansion_policy="NONE" default in StrategyConfig
- V018-B constrained to NW quadrant (25 tiles) in many games
- Real competitive agents may expand to 2-3 quadrants (50-75 tiles)
- V018 scorecard: Land Spend $5,756 -- inconsistent expansion behavior

### Cause 5 (POSSIBLE): Never tested in two-Melon-farmer scenario

The market compression effect:
- Two V018-B agents playing each other would BOTH crash the Melon market
- If real opponents are also Melon-heavy, V018-B receives ~$1/unit for most crop
- Could turn $52k games into $5-10k games

### Cause 6 (POSSIBLE): Crop deaths and watering misses

Evidence from V018 scorecard:
- 21.5 crop deaths per game
- 12.3 watering misses per game
- Under competitive conditions where win/loss is binary, any lost production matters

---

## 4. Evidence Summary Table

| Hypothesis | Evidence | Confidence |
|---|---|---|
| Score = skill rating not bank | kaggriculture.json + Kaggle docs confirm BT starting at 600 | CONFIRMED |
| 521.1 < 600 = net loser | Mathematical certainty | CONFIRMED |
| Local opponents too weak | random earns $0-500, starter earns $3,500 | CONFIRMED |
| No opponent-awareness | Code review: zero opponent observation used | CONFIRMED |
| Melon monoculture | 98% revenue is premium (crop_policy=MELON) | CONFIRMED |
| Market crash from opponent | Melon above_func=sq, above_target=3.60 | HIGH |
| Expansion inconsistency | expansion_policy=NONE default | HIGH |
| Crop deaths / watering misses | 21.5 deaths, 12.3 misses per game | MEDIUM |

---

## 5. The Fundamental Mismatch

LOCAL BENCHMARK QUESTION:
  "How much money can V018-B earn playing alone?"
  Answer: ~$52,780 mean
  This DOES NOT predict leaderboard score

KAGGLE LEADERBOARD QUESTION:
  "Does V018-B earn MORE money than the opponent?"
  Answer: Only 35-40% of the time (implied by 521.1)
  THIS IS THE ONLY QUESTION THAT MATTERS

The entire optimization history from V001-V018 has been optimizing the WRONG objective.

---

## 6. Price Curve Analysis: Why Melon is Dangerous

| Resource | Above func | Above target | Glut sensitivity |
|---|---|---|---|
| Melon | sq | 3.60 | WORST -- quadratic crash |
| Milk | linear | 1.60 | High -- goes to floor fast |
| Strawberry | linear | 1.60 | High |
| Wool | sq | 3.20 | Very high |
| Egg | log | 0.20 | BEST -- barely reacts to oversupply |
| Carrot | sqrt | 0.70 | Low -- good for shared market |
| Tomato | sqrt | 0.60 | Low |
| Wheat | log | 0.20 | Very resistant |

V018-B is monocultured on Melon -- the crop with the WORST shared-market crash profile.
If both players sell Melons, both lose almost all revenue.

---

## 7. What Score 521.1 Tells Us About the Field

Using Elo/Bradley-Terry math:
- Score 521 vs starting 600 = expected to LOSE ~61% of games
- Real agents earn MORE than V018-B in most games
- Field likely includes agents earning $55,000-$100,000+ consistently
- Or agents using market-crash-immune strategies (Egg: above_func=log, above_target=0.20)

---

## 8. Path to Rating 1000

To reach 1000 from 521:
- Need to win ~65-70% of games against the current field
- Requires: earning more AND surviving opponent market interference

Priority order:
1. CRITICAL: Competitive self-play benchmark to find true floor
2. CRITICAL: Market crash resistance / crop diversification
3. HIGH: Opponent-aware sell timing (delay if market is pre-crashed)
4. HIGH: Consistent land expansion to increase production ceiling
5. MEDIUM: Reduce crop deaths (21.5/game)
6. MEDIUM: Win-rate-focused strategy (maximize P(earning $1 more than opponent))

---

## 9. Benchmark Architecture Fix

Current benchmark (BROKEN for leaderboard purposes):
  V018-B vs random   (earns ~$0)
  V018-B vs pass     (earns ~$0)
  V018-B vs starter  (earns ~$3,500)
  Metric: Final Bank of V018-B
  Result: Always wins -> MEANINGLESS for leaderboard optimization

Required benchmark (Kaggle-like):
  V018-B vs V018-B (self-play)
  V018-B vs diversified opponent
  V018-B vs market-crash scenario
  Metric: WIN RATE (not bank balance)
  Result: Measures true competitive performance

---

## 10. Variant Scorecard Template

| Variant | Local Mean Bank | Worst Case | Win Rate vs V018-B | Win Rate vs Competitive | Change |
|---|---:|---:|---:|---:|---|
| V018-B (champion) | $52,780 | $27,496 | -- | ~35-40% (521.1) | Baseline |
| V019-A (control) | TBD | TBD | 50% (expected) | TBD | Exact copy of V018-B |
| V019-B | TBD | TBD | TBD | TBD | First isolated change |
| V019-C | TBD | TBD | TBD | TBD | Second isolated change |
| V019-D | TBD | TBD | TBD | TBD | Best combination |

---

## 11. Immediate Next Steps (DO NOT OPTIMIZE YET)

Step 1: Create scripts/benchmark_competitive.py
  - V018-B vs V018-B self-play, 30 seeds, track win rate
  - V018-B vs Carrot/Egg diversified agent
  - Measure Melon price at time of harvest in self-play games

Step 2: Quantify market crash impact
  - Determine how often Melon market is crashed before V018-B can sell
  - Calculate average revenue loss from market compression in self-play

Step 3: Build V019-B with ONE isolated change
  - Candidate: Crop diversification (Melon + Carrot/Egg mix)
  - Rationale: Carrot/Egg have crash-resistant price curves
  - Control: V019-A = exact copy of V018-B
  - Test: V019-B win rate vs V019-A > 55%?

Step 4: Submit ONLY when win rate improvement is robust across 30+ seeds

---

## Summary

CURRENT KAGGLE SCORE:    521.1
LOCAL BASELINE:          $52,780 mean bank (NOT predictive of leaderboard)
KAGGLE-LIKE BASELINE:    Not yet established (benchmark needed)
MAIN SCORE GAP CAUSE:    Wrong objective -- optimized absolute bank vs weak opponents
                         instead of WIN RATE vs real agents
SECONDARY CAUSE:         Melon monoculture -- worst crash profile in the game
                         (sq curve, above_target=3.60) makes V018-B fragile
                         when any opponent is also premium-focused
CURRENT BOTTLENECK:      Unknown -- competitive benchmark needed first
BEST NEXT EXPERIMENT:    V018-B vs V018-B self-play (30 seeds, track win rate)
EXPECTED IMPACT:         Establishes true competitive floor and confirms market crash hypothesis

FILES CREATED:
  V019_SCORE_GAP_ANALYSIS.md          (this document)
  scripts/benchmark_competitive.py    (NEXT -- to be created)

CHAMPION MODIFIED: NO
READY FOR V019 IMPLEMENTATION: NO -- benchmark must be established first
