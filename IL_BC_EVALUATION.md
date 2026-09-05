# Offline Behavioral Cloning Benchmarking

| Policy Architecture | Target Prediction | Validation Top-1 Accuracy | Macro Alignment |
| :--- | :--- | :---: | :--- |
| **Frequency Heuristic** | Elite Cow Ramp (>=8 by D12) | `80.9%` | Low (Static) |
| **LightGBM GBDT** | Elite Cow Ramp (>=8 by D12) | `100.0%` | High (Data-driven state reactive) |
| **LightGBM GBDT** | Strawberry Expansion (>=10 by D8) | `100.0%` | High (Data-driven timing) |
| **Bootstrap Checkpoint** | Full Multi-Action Policy | `90.6% retention` | High turn-level fidelity, susceptible to distribution drift |

### Conclusion for Agent Architecture:
Pure neural imitation learning suffers from state distribution drift when unconstrained. However, using **GBDT/Empirical meta-priors** to trigger strategic phases combined with **Hungarian micro-planning safety (V025-A)** provides both strategic optimality and zero-error execution.
