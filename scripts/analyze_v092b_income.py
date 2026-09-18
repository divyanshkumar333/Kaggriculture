"""Analyze the v092b replay's income sources day by day."""
import json, base64, zlib

with open('agents/v092b_replay_seed.py', 'r') as f:
    code = f.read()

start = code.find("b85decode(\n    '") + len("b85decode(\n    '")
end = code.find("'", start)
actions = json.loads(zlib.decompress(base64.b85decode(code[start:end])))

# Track market income sources
print("=== Income by Source (Day 0-15) ===")
for day in range(16):
    start_step = day * 24
    fert_sold = 0
    wool_sold = 0
    wheat_sold = 0
    milk_sold = 0
    straw_sold = 0
    melon_sold = 0
    hires = 0
    animals_bought = []
    land_bought = 0
    seeds_bought = {}
    
    for h in range(24):
        step = start_step + h
        if step >= len(actions): break
        market = actions[step].get('market', [])
        for op in market:
            if not op: continue
            if op[0] == 'SELL':
                item, qty = op[1], op[2] if len(op) > 2 else 1
                if item == 'FERTILIZER': fert_sold += qty
                elif item == 'WOOL': wool_sold += qty
                elif item == 'WHEAT': wheat_sold += qty
                elif item == 'MILK': milk_sold += qty
                elif item == 'STRAWBERRY': straw_sold += qty
                elif item == 'MELON': melon_sold += qty
            elif op[0] == 'HIRE': hires += 1
            elif op[0] == 'BUY_ANIMAL': animals_bought.append(op[1])
            elif op[0] == 'BUY_LAND': land_bought += 1
            elif op[0] == 'BUY_SEED': seeds_bought[op[1]] = seeds_bought.get(op[1], 0) + op[2]
    
    sold = []
    if fert_sold: sold.append(f'fert={fert_sold}')
    if wool_sold: sold.append(f'wool={wool_sold}')
    if wheat_sold: sold.append(f'wheat={wheat_sold}')
    if milk_sold: sold.append(f'milk={milk_sold}')
    if straw_sold: sold.append(f'straw={straw_sold}')
    if melon_sold: sold.append(f'melon={melon_sold}')
    
    bought = []
    if animals_bought: bought.append(f'animals={animals_bought}')
    if land_bought: bought.append(f'land={land_bought}')
    if seeds_bought: bought.append(f'seeds={dict(seeds_bought)}')
    
    print(f"  Day {day:2d}: hires={hires} SOLD=[{', '.join(sold)}] BOUGHT=[{', '.join(bought)}]")
