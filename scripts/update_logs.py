import re

log_path = 'RESEARCH/experiment_log.md'
with open(log_path, 'r') as f:
    log_data = f.read()

# Replace the PLANNED EXP-036 with the actual results
exp036_result = '| **EXP-036** | 2026-09-20 | V101_TerminalLiquid | CHAMPION_main | 4 / 8 | 0 - 0 - 8 | 0.0% | -,645 | **REJECTED (FrontRun is already optimal)** |'
log_data = re.sub(r'\|\s*\*\*EXP-036\*\*.*PLANNED\s*\|', exp036_result, log_data)

# Add EXP-037 for Prisoner's Dilemma resolution
exp037_planned = '| **EXP-037** | TBD | V102_PrisonerResolution | CHAMPION_main | 8 | TBD | TBD | TBD | TBD | TBD | PLANNED |\n'
log_data += '\n### EXP-036: Terminal Liquidation — REJECTED\n- Hypothesis: Ignored trace and dumped shed on Day 25+ to extract margin.\n- Result: Failed across 7 variants (V106-V112, V101). Mean loss -.\n- Root Cause: Champion\'s _front_run already optimally liquidates the shed immediately upon harvest. Stripping trace actions (like HIRE) causes unharvested yield to rot, creating a net loss.\n\n### EXP-037: Prisoner\'s Dilemma Resolution — PLANNED\n- Target: Resolve the -.4k loss to public_v16_rc5 by tuning the 30-day front-run depth to avoid symmetric market crashing.\n'

with open(log_path, 'w') as f:
    f.write(log_data)

lessons_path = 'RESEARCH/LESSONS.md'
with open(lessons_path, 'r') as f:
    lessons = f.read()

new_lesson = '''
### L009: Champion is Already an Optimal Terminal Liquidator
Attempts to override main.py's terminal phase (Day 25+) with manual dumping or holding (EXP-036 series) consistently lose by -. The champion's combination of _front_run (which pulls future trace sales to the moment of harvest) and _rank_sell_slots acts as a perfect continuous liquidator. Manually overriding the trace's HIRE or CARE actions in the terminal phase causes unharvested yield to rot, resulting in a net loss.
'''
lessons += new_lesson

with open(lessons_path, 'w') as f:
    f.write(lessons)
