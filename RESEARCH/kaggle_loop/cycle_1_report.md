# Cycle 1 Report

## The 5 Candidates

1. **Candidate 1: V057 Generalized Market Spoiler Detection**
   - *Hypothesis:* Detecting opponent inventory via global market deltas and reacting dynamically to front-run them will beat a static front-run.
   - *Kaggle Rating:* 1187.7
   - *Result:* **SUCCESS**. This is the highest rating achieved so far.
2. **Candidate 2: V058 Replay Meta (Early Cows + Strawberries)**
   - *Hypothesis:* Avoiding the Melon crash entirely by opening with Cows and Strawberries will provide consistent, un-griefable equity.
   - *Kaggle Rating:* 635.0
   - *Result:* **FAILED**. Skipping Melons meant missing out on $27,500 on Day 10, preventing the agent from buying the rest of the board.
3. **Candidate 3: V059 Pure Strawberry Flywheel**
   - *Hypothesis:* A purely dynamic, worker-assigning Strawberry agent will efficiently monopolize the late-game market without the rigidness of V16.
   - *Kaggle Rating:* 274.1
   - *Result:* **FAILED**. Terribly. Dynamic task allocation was severely suboptimal compared to the heavily optimized static paths of V16.
4. **Candidate 4: V060 Melon Frontrunner**
   - *Hypothesis:* Forcefully dumping all Melons on Hour 0 of Day 10 will dodge the crash and generate maximum cash to fuel V16's static expansion.
   - *Kaggle Rating:* 1005.4
   - *Result:* **MIXED**. It improved upon the 600-rated baseline, but lost to V057. A static front-run leaves money on the table if the opponent isn't actually contesting the market.
5. **Candidate 5: V064 Adaptive Depth 18**
   - *Hypothesis:* A shorter Lookahead (Depth 18 vs Depth 30) will create a divergent, more reactive pathing algorithm.
   - *Kaggle Rating:* 990.2
   - *Result:* **MIXED**. Highly competitive, but ultimately slightly worse than V060 and much worse than V057.

## Key Learnings
1. **Dynamic > Static (When it comes to Market Manipulation).** V057 proved that reacting to the opponent's *actual* inventory is strictly superior to blindly assuming they will crash the market.
2. **Melon Opening is Non-Negotiable.** V058 and V059 completely skipped Melons and were heavily punished. 

## Next Research Direction (Cycle 2)
The next step is to perform an ablation study on V057, as requested by the user. If a new candidate improves over a champion, we must not immediately stack more mechanisms onto it. We must identify what actually caused the improvement. 

V057 is technically just V051 (Lookahead 30) with the `_future_target` logic swapped out to track the opponent's shed. 
To fully understand V057, I must build ablations of V057:
- **Ablation 1:** V057 but it ONLY tracks Melons (ignores Strawberries).
- **Ablation 2:** V057 but it ONLY tracks Strawberries (ignores Melons).
- **Ablation 3:** V057 but it uses V052 (Depth 18) as the base instead of V051 (Depth 30).
- **Ablation 4:** V057 but it pulls the sale forward by TWO turns instead of one turn (front-running the front-runners).
- **Ablation 5:** An Adversarial V057 that intentionally crashes the market *after* the opponent sells (Wait, no, that makes no sense).

I will design the Cycle 2 Submissions around V057 ablations.
