# Source of Truth Hierarchy

In this repository, a confident statement in Markdown does **NOT** override a reproducible counterexample. To navigate the extensive but often contradictory research logs, the following strict hierarchy of truth is established:

## 1. Executable Code
The actual Python source code (`.py`) deployed in `agents/` and `main.py` is the ultimate arbiter of what a candidate does. If a Markdown report claims a strategy uses a "Hungarian safety shield" but the code uses greedy nearest-neighbor, the code is the truth.

## 2. Reproducible Local Experiment
A local match run via a unified harness (`RESEARCH/harness/run_match.py`) across paired seeds and both seat assignments overrides any previous numerical claim. If a report claims an 85% win rate, but a reproducible sweep yields 45%, the local reproducible sweep is the truth.

## 3. Actual Kaggle Replay / Submission Result
Live episode outcomes on the Kaggle servers (JSON replay files) provide ground-truth environment behavior, including edge cases (e.g., turn-0 execution, true step accessor mechanics) that might differ from local simulator approximations. They also prove whether an agent actually achieved a rating.

## 4. Raw Dataset
The `KiroSamurai/kaggriculture-il` dataset (when parsed correctly) serves as the basis for empirical claims about top competitors. Assertions about the meta must be backed by reproducible parsing of this dataset.

## 5. Research Report
Markdown analysis reports (`CAUSAL_VALIDATION_REPORT.md`, etc.) are treated as hypotheses and historical context. Their claims are considered unverified until confirmed by levels 1-4.

## 6. README Prose
General repository documentation provides overarching intent but is the least reliable source for mechanistic or competitive claims.
