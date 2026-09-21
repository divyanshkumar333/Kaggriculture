# V104 Kaggle Forensics Audit

## Executive Finding: Submission Status

- **Candidate**: `agents/v104_quote_priority.py`
- **Local Artifacts**:
  - `submission_v104_quote_priority.py` (5,759 lines, SHA256 verified)
  - `submission_v104_quote_priority.tar.gz` (521,002 bytes)
  - Committed in git commit `2b3a7c1255cadfdf60a18fce831f5ebc0b873c41` on Mon Sep 21 01:34:09 2026 +0530.
- **Kaggle API State**:
  - Direct query of Kaggle Submissions API (`api.competition_submissions('kaggriculture')`) reveals that **V104 was packaged locally but NOT submitted to the Kaggle servers**.
  - The most recent Kaggle submission remains `56403931` (`submission_v058_challenger.tar.gz`) submitted on 2026-09-20 18:46:04 UTC.
  - Zero ladder matches, zero ladder replays, and zero ladder losses exist for V104 on Kaggle because it has not yet been submitted.

## Current Active Submissions on Kaggle

| Ref | Package / Name | Submitted (UTC) | Rating (Score) | Episodes | Status |
|:---|:---|:---|:---|:---|:---|
| **56403931** | `submission_v058_challenger.tar.gz` | 2026-09-20 18:46:04 | **958.0** | 95 | Active (Challenger Slot) |
| **56403913** | `submission_v057_control.py` | 2026-09-20 18:45:09 | **895.0** | 93 | Active (Control Slot) |

## Forensic Implication

Because V104 has 0 Kaggle episodes, the reported 44W / 0L / 6D record is **exclusively local tournament evidence**.
Per Rule 21 and the primary objective:
- We do NOT claim any Kaggle rating or generalization for V104 until it is submitted and validated on the live ladder.
- Per Third Task, before any submission or further modification, we must conduct strict **causal validation** comparing V104 Control (unmodified 2945 farm) against V104 Quote Priority on identical seeds and opponents, measuring market revenues and cash outcomes.
