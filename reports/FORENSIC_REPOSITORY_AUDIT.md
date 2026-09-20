# Forensic Repository Audit

## A. What is actually in GitHub origin/main?
The `origin/main` branch is entirely synced with the local `main` branch. All files, including the extensive `agents/` directory containing iterations from `v001` through `v096`, are pushed.

## B. What exists locally but is not pushed?
The `git status` reflects that the working tree is completely clean and up to date with `origin/main`. There are no untracked or uncommitted research files.

## C. What is currently considered production?
`main.py` is the standard entry point for Kaggle submissions. The most recent git logs indicate that **V051 (Lookahead 30)** was promoted as the "Final 2900+ Kaggle Candidate". However, the docstring in `main.py` references "Agent V032: V031 + 4-Step Front-Running Lookahead", suggesting the documentation inside `main.py` may not have been correctly updated to reflect the `V051` logic, or `main.py` was overwritten after `V051` was promoted. (Further investigation is required, see SOURCE OF TRUTH).

## D. What is experimental?
Everything in `agents/` and `experiments/` is experimental.
Recent logs explicitly mention rejecting **V055** and **V056**.
Versions up to **v096** exist in `agents/`, indicating that experimental iterations advanced far beyond the V051 production candidate (e.g., `v096_12melon_opening.py`, `v094_hybrid_a.py`).
`026_the_golden_ratio.py` is also experimental despite its confident naming.

## E. What is obsolete?
Any agent explicitly rejected in commit logs (e.g., V055, V056), as well as earlier iterations leading up to V051 (such as V001 through V031), unless they represent a fundamentally different architectural branch (e.g. `v013_robust_trace.py`) that hasn't been strictly superseded by Lookahead strategies.
The previous midgame router error (noted in the prompt, possibly `V057`) is considered obsolete.
