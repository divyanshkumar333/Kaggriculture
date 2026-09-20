# Live vs Local Gap Analysis

## Overview
Recent submissions (e.g., V099, V098, V097) have underperformed on the live Kaggle ladder despite showing strong local win rates against older submissions (like V057 and main-line agents). This report diagnoses the discrepancy between our local analytical assumptions and the true live environment.

## Diagnosis Matrix

| Factor | Local Assumption | Live Reality | Gap Impact |
|--------|------------------|--------------|------------|
| **Meta Composition** | Local meta is heavily skewed towards variants of our own agents (e.g., cow rush, melon spam). | Live meta has highly diverse, unknown architectures (e.g., public 3000+ notebooks like Kaito's 25/27 Strict-Future or Roman Rozen's Barnyard Economist). | **High**: Overfitting to our own specific playstyles leads to fragile routing and price assumptions. |
| **Price Dynamics** | Prices often crash predictably based on our own agent's production choices. | Competitors often actively counter-speculate, causing unexpected price floors or sudden scarcity. | **Critical**: Terminal liquidation logic based on expected price decay fails when the market behaves contrarian. |
| **Shop Draws** | Evaluated on fixed, small seed pools (e.g., 8-32 seeds) leading to memorization of shop unlocking. | True uniform random with replacement over 720 steps creates high-variance shop unlocks. | **Medium**: Agents hardcoding shop expectations will fail in edge-case distributions. |
| **Terminal Behavior** | Sheds are efficiently liquidated on step 718 under the assumption of stable endgame demand. | Top opponents often front-run terminal sell-offs on steps 715-717, crashing prices before our agent acts. | **Critical**: V099 likely lost 10-20% of its final score simply by selling 1 step too late in contested markets. |

## Conclusion
The local advantage of V099 was an illusion created by overfitting to a specific subset of the game tree. Live results show that V057's *generalized spoiler* behavior is more robust against unknown 3000+ architectures. We must halt the progression of V099-style logic until the benchmark incorporates a wider variety of these public 3000+ behaviors and we evaluate on strictly out-of-sample `PROMOTION` seed blocks.
