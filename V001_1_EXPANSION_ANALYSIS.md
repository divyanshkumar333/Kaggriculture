# V001.1 Land Expansion Experiment Analysis

## Hypothesis
If the agent calculates the expected return on investment (ROI) for land expansion and purchases new quadrants dynamically, the overall production capacity will scale, leading to a significantly higher final bank balance compared to the 25-tile hard cap.

## 1. Experimental Setup

*   **Control (V001.1-control):** `v001_baseline.py` (Exact economics, consumable-aware task generation, NO land expansion).
*   **Expansion (V001.1-expansion):** `v001_expansion.py` (Same as control, but with ROI-based evaluation of NE, SW, SE land expansion).
*   **Opponents:** `random`, `starter`, `melon_maxxer`
*   **Trials:** 10 deterministic games per opponent (seeds 42-51) for a total of 30 games per variant.

## 2. Benchmark Results

### Overall Economics
| Metric | V001.1-control | V001.1-expansion | Diff |
| :--- | :--- | :--- | :--- |
| **Mean Final Bank** | $TBD | $TBD | $TBD |
| **Total Revenue** | $TBD | $TBD | $TBD |
| **Total Spending** | $TBD | $TBD | $TBD |
| **Seed Spending** | $TBD | $TBD | $TBD |
| **Land Spending** | $TBD | $TBD | $TBD |
| **Worker Cost** | $TBD | $TBD | $TBD |

### Production Metrics
| Metric | V001.1-control | V001.1-expansion | Diff |
| :--- | :--- | :--- | :--- |
| **Melons Planted** | TBD | TBD | TBD |
| **Melons Harvested** | TBD | TBD | TBD |
| **Melons Sold** | TBD | TBD | TBD |
| **Land Purchased** | 0.0 | TBD | TBD |

### Worker Utilization
| Metric | V001.1-control | V001.1-expansion | Diff |
| :--- | :--- | :--- | :--- |
| **Workers Hired** | TBD | TBD | TBD |
| **Idle Turns** | TBD | TBD | TBD |
| **Movement Actions** | TBD | TBD | TBD |
| **Useful Actions** | TBD | TBD | TBD |
| **Worker Util %** | TBD% | TBD% | TBD% |
| **Farmer Util %** | TBD% | TBD% | TBD% |

## 3. Worker Drop Investigation

The control benchmark revealed a large number of worker idle turns (~1,074 per game). 

**Why are workers idle?**
*TBD based on the data.*

**Are they waiting for tasks?**
*TBD*

**Are tasks unavailable because seeds are unavailable?**
*TBD*

## 4. ROI Analysis

*   **Marginal Revenue:** $TBD
*   **Marginal Costs (Land + Worker + Seed):** $TBD
*   **Actual ROI:** TBD%

## 5. Conclusion & Decision Rule

**Decision:** TBD (Preserve as new candidate / Reject hypothesis)

**Reasoning:**
TBD

## 6. Next Recommended Experiment
TBD
