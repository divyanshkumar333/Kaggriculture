# V020 Competitive Intelligence & Kaggle Simulation Dynamics

## Executive Summary

| Metric | Status |
|---|---|
| **Submitted Champion** | `agents/v018_b_batch_cap.py` (`main.py` / `agents/v020_a_control.py`) |
| **Initial Leaderboard Score** | **600.0** |
| **Current Target** | **1000.0** |
| **Long-Term Target** | **3000.0** |
| **Evaluation Type** | 2-Player Head-to-Head Bayesian Skill Rating (Elo / Bradley-Terry) |
| **Season Duration** | 720 turns (30 days $\times$ 24 turns/day) |
| **Core Discrepancy** | High single-player profit ($\sim \$52k$) vs. Competitive Fragility ($\sim 20\text{--}35\%$ win rate in symmetric markets) |

---

## 1. Competitive Architecture & Leaderboard Mechanism

1. **TrueSkill / Bradley-Terry Rating Model**:
   - Each submission enters at **600.0**.
   - Matchmaking pairs agents of similar rating.
   - Outcome is strictly binary/ternary: **Win (+), Loss (-), Tie (0)**.
   - Margin of victory does **not** matter (winning by \$1 equals winning by \$50,000).
   - Rating converges after $\sim 60$ matches.

2. **The Shared Market Vulnerability**:
   - Both players buy seeds from fixed-price shops, but sell produce into a **shared market pool ($I_0 = 10,000$)**.
   - **Melon** has the steepest quadratic crash curve in the game:
     $$\text{Melon Curve: } \text{above\_func} = \text{sq}, \text{above\_target} = 3.60$$
   - A combined volume of $>150$ Melons drops the price from $\$250$ to $\$1.0$ floor.
   - Town shops unlock every 3 days (drawn with replacement, up to 8 instances) and consume 1 unit every 4 turns ($\sim 6$ units/day per shop instance), creating partial price recoveries throughout the mid-to-late season.

3. **Major Competitor Archetypes**:
   - **Type A: Pure Melon Monoculture (like V018-B)**: Maximizes yield in uncontested games, but mutually destructive in symmetric matchups.
   - **Type B: Industrial Livestock / Animals (Cows, Sheep, Geese)**: Steady recurring yield without replanting/watering overhead. Produces Eggs/Milk/Wool with crash-resistant log/linear price curves.
   - **Type C: Dynamic Multi-Crop Diversifier**: Balances Carrots, Tomatoes, and Melons across multiple land quadrants.
   - **Type D: Aggressive Land Maximizer**: Rapidly purchases NE/SW/SE quadrants to scale tile count from 25 to 50–100 tiles.

---

## 2. Competitive Intelligence on V018-B / V020-A Control

### Strengths:
- Highly optimized Hungarian bipartite matching for spatial movement.
- Dynamic labor allocation (hiring farmhands when task deficit $> 0$).
- Batch cap ($4$ seeds/day) preventing severe opening market oversaturation.
- 100% win rate against naive / starter / greedy single-farmer bots.

### Confirmed Bottlenecks:
1. **Symmetric Market Suicide**: When facing another Melon-heavy bot, both players crash the Melon market to $\$1.0$, reducing bank from $\$52k$ to $\$6k\text{--}\$33k$.
2. **Late-Season Inertia**: Continuing to buy long-cycle seeds after Day 20 when they cannot reach max yield or mature in time.
3. **Land Expansion Delay**: Land expansion is often delayed until cash $> \text{cost} + 2000$, keeping the agent constrained to 25 tiles.
4. **Endgame Liquidation**: Leaving unharvested crops or unsold inventory on Day 29.
