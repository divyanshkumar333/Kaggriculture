"""
Find which layer in the 41-layer stack causes the WHEAT OSCILLATION pattern:
- Step 2: SELL WHEAT 5
- Step 3: BUY WHEAT 5
- Step 4: SELL WHEAT 4
- ...
This alternation blocks all other market orders for 20 steps.
"""
import re

with open(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', encoding='utf-8') as f:
    lines = f.readlines()

content = ''.join(lines)

# Find the layer that generates the alternating pattern
# Pattern: "SELL" and "WHEAT" near "BUY_PRODUCT" and "WHEAT" in a loop
# Look for: patterns like wheat_sell_qty decreasing, or alternating sell/buy

# Scan each def agent for sell-wheat / buy-wheat-product logic
def_agent_positions = []
for i, line in enumerate(lines):
    if line.strip().startswith('def agent('):
        def_agent_positions.append(i+1)  # 1-indexed

print(f"Found {len(def_agent_positions)} 'def agent' functions")
print("Lines:", def_agent_positions[:10], "...")

# Look for the specific sell/buy wheat oscillation pattern
# Key words: 'SELL', 'WHEAT', 'BUY_PRODUCT' in proximity with quantity math
oscillation_candidates = []
for i, line in enumerate(lines):
    if 'SELL' in line and 'WHEAT' in line and 'BUY_PRODUCT' in line:
        oscillation_candidates.append(i+1)
        print(f"Line {i+1}: {line.rstrip()[:120]}")

print(f"\nLines with SELL+WHEAT+BUY_PRODUCT: {len(oscillation_candidates)}")

# Also look for sell_qty type patterns
print("\n=== DECREASING SELL QUANTITY PATTERNS ===")
for i, line in enumerate(lines):
    # Look for patterns like "wheat_qty -= 1" or "sell_qty" with wheat
    if ('wheat' in line.lower() or 'WHEAT' in line) and any(word in line for word in ['qty', 'count', 'amount', '-=', 'reduce', 'decrement']):
        print(f"Line {i+1}: {line.rstrip()[:120]}")

# Find all locations where 'SELL' and 'WHEAT' and buy_product appear together in a block
print("\n=== SELL WHEAT GENERATION CONTEXT ===")
for i, line in enumerate(lines):
    if "'SELL'" in line and 'wheat' in line.lower() and i > 900:
        start = max(0, i-3)
        end = min(len(lines), i+5)
        print(f"\n--- Block at line {i+1} ---")
        for j in range(start, end):
            print(f"{j+1}: {lines[j].rstrip()[:120]}")
