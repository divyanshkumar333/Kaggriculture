# Kaggle Scoring Determinism

To understand why local results and Kaggle results mismatched, we must model the true objective function of the Kaggriculture environment.

## 1. The Rating System
Kaggle simulation competitions use a Bayesian rating system (typically a variant of TrueSkill or Glicko). The score (e.g. 1187.7) is NOT an absolute measure of cash generated. It is an ELO-style rating representing the probability of beating other agents in the active pool.
- **Convergence:** An agent starts with a provisional rating (often around 600) and it takes dozens or hundreds of episodes to converge.
- **Population Dependence:** The rating is completely dependent on the meta of the active pool. An agent that generates $150k but loses to the current meta (because they both crash the market and the opponent edges out a win) will have a lower rating than an agent that generates $60k but consistently beats the meta.

## 2. Types of Mismatch (Local vs Kaggle)
- **A. Deterministic Engine Performance:** Is the code deterministic? Yes. `v16` and its wrappers are highly deterministic unless random opponent actions disrupt their pathing.
- **B. Randomized Opponent Selection:** On Kaggle, you don't pick your opponent. You are matched randomly based on rating proximity. If you are rated 1000, you will play other 1000-rated agents. If those agents are all V16 clones, and your agent beats V16, your rating climbs. If you hit a wall of 1200-rated agents playing a completely different strategy (e.g., Tomato spam) that happens to counter you, your rating will stall.
- **C. Changing Opponent Population:** As top players submit new agents, the meta shifts. What worked yesterday might not work today if the population adopts a counter-strategy.
- **D. Rating Convergence:** A newly submitted agent might have a high score after 5 games (lucky matches) but drop after 50 games. We must wait for convergence.
- **F. Actual Stochasticity:** The environment itself has minor stochasticity (weed spawn chance, shop unlocks). More importantly, the *timing* of actions between two identical agents depends on the player seat (Player 1 processes before Player 2 in identical ticks, or vice-versa depending on the engine).

## 3. Why V057 (1187.7) beat V060 (1005.4)
Both V057 and V060 are Melon Frontrunners. But they operate differently:
- **V060** is static. It blindly dumps Melons on Hour 0 of Day 10, regardless of the opponent.
- **V057** is dynamic. It infers the opponent's shed by tracking the shared market. It ONLY dumps when it mathematically confirms the opponent is hoarding. 

Why did dynamic beat static? Because if the opponent is *not* playing Melons, V060 dumps on Hour 0, getting a good price, but missing out on the absolute maximum price it could have gotten if it waited for Town Center demand (since it has a monopoly). V057 waits if there is no threat, maximizing profit when it has a monopoly, but front-running when there is a threat. 
*Hypothesis:* V057 has a higher win rate against non-meta agents, allowing it to climb higher in the ELO bracket.

## 4. Conclusion
Kaggle rating is a measure of **expected win rate against the current active population**. To reach 3000+, we must not only beat V16, but we must beat whatever agents the top players are using to beat V16.
