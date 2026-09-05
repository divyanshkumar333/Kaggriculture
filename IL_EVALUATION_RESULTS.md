# IL Policy Evaluation Tournament Results

**Date:** September 5, 2026  
**Configuration:** 15 Paired Seeds (30 games per pairing) across 8 parallel worker processes.

## 1. Candidate vs V025-A Head-to-Head

| Candidate | Win Rate (%) | Candidate Mean ($) | V025-A Mean ($) | Net Margin ($) | Candidate Median ($) | P10 ($) | P90 ($) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `v026_a_il_hybrid` | **63.3%** | $50,542 | $48,757 | **$+1,785** | $49,620 | $32,169 | $77,936 |
| `v026_b_il_gbdt` | **23.3%** | $52,939 | $67,715 | **$-14,776** | $53,372 | $43,467 | $61,940 |
| `v026_c_il_pure_imitation` | **86.7%** | $57,398 | $51,443 | **$+5,955** | $53,963 | $43,366 | $81,560 |
| `v026_d_il_conservative` | **33.3%** | $48,912 | $53,588 | **$-4,676** | $48,134 | $33,019 | $64,725 |

## 2. V026-A vs Historical Benchmark Suite

| Opponent | Win Rate (%) | V026-A Mean ($) | Opponent Mean ($) | Net Margin ($) |
| :--- | :---: | :---: | :---: | :---: |
| `v023_g_capital_optimizer` | **83.3%** | $70,858 | $60,352 | **$+10,506** |
| `v022_c_market_batching` | **100.0%** | $70,761 | $43,530 | **$+27,231** |
| `v020_c_submission_candidate` | **100.0%** | $89,048 | $45,702 | **$+43,346** |
| `v021_b_industrial_livestock` | **100.0%** | $91,152 | $22,153 | **$+68,999** |
