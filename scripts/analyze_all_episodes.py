"""
Analyze ALL downloaded Kaggle episode replays.
For each episode: identify which player is our 013 agent (uses BUY 14 WHEAT)
and which is the opponent. Extract the opponent's strategy when they win.
"""
import json, base64, zlib, os

def load_trace_from_agent(path):
    with open(path, 'r') as f:
        code = f.read()
    start = code.find("base64.b85decode(") + len("base64.b85decode(")
    q1 = code.find("'", start)
    q2 = code.find("'", q1 + 1)
    return json.loads(zlib.decompress(base64.b85decode(code[q1+1:q2])))

# Load our agent's trace to compare
our_trace = load_trace_from_agent('agents/013_robust_trace.py')

# Our Day 0 H0 market: the first market action at step 0 is a fingerprint
our_step0_market = our_trace[0].get('market', [])  # this is what 013 does at step 0

replay_dir = 'replays'
episodes = sorted(
    [f for f in os.listdir(replay_dir) if 'replay' in f and f.endswith('.json')],
    key=lambda x: int(x.split('-')[1]), reverse=True
)

print(f"Analyzing {len(episodes)} episodes\n")
print("Our Step 0 market:", our_step0_market[:3])
print()

wins = []
losses = []

for fname in episodes:
    try:
        with open(f'{replay_dir}/{fname}') as f:
            data = json.load(f)
        steps = data['steps']
        p0_final = steps[-1][0]['reward']
        p1_final = steps[-1][1]['reward']
        
        # Step 1 contains the actions taken at step 0
        p0_step0 = (steps[1][0].get('action') or {}).get('market', [])
        p1_step0 = (steps[1][1].get('action') or {}).get('market', [])
        
        # Detect which player is us (matches our step 0 market)
        def markets_match(m1, m2):
            return m1[:1] == m2[:1]  # first order is distinctive
        
        if markets_match(p0_step0, our_step0_market):
            our_idx = 0
            our_score = p0_final
            opp_score = p1_final
            opp_step0 = p1_step0
        elif markets_match(p1_step0, our_step0_market):
            our_idx = 1
            our_score = p1_final
            opp_score = p0_final
            opp_step0 = p0_step0
        else:
            our_idx = -1  # can't identify
            our_score = max(p0_final, p1_final)
            opp_score = min(p0_final, p1_final)
            opp_step0 = []
        
        ep_id = fname.split('-')[1]
        won = our_score > opp_score
        result = "WIN" if won else "LOSS"
        
        # Analyze opponent's Day 0 strategy
        opp_wheat = sum(op[2] for op in opp_step0 if len(op)>2 and op[0]=='BUY_PRODUCT' and op[1]=='WHEAT')
        opp_hires_d0 = sum(1 for op in opp_step0 if op[0]=='HIRE')
        
        # More opponent detail from days 1-5
        opp_d15_market = []
        for step in steps[2:121]:  # steps 1-120 (days 1-5)
            opp_m = (step[1 - (1-our_idx) if our_idx >= 0 else 0].get('action') or {}).get('market', []) if our_idx >= 0 else []
            opp_d15_market.extend(opp_m)
        
        opp_sells = [(op[1], op[2]) for op in opp_d15_market if op[0]=='SELL'][:5]
        
        print(f"Ep {ep_id}: {result} | us={our_score:.0f} opp={opp_score:.0f} | gap={our_score-opp_score:.0f}")
        print(f"  Our idx=P{our_idx if our_idx>=0 else '?'} | Opp D0: wheat={opp_wheat} hires={opp_hires_d0}")
        print(f"  Opp D0 market: {opp_step0[:4]}")
        if opp_sells:
            print(f"  Opp D1-5 sells: {opp_sells}")
        
        if won:
            wins.append((ep_id, our_score, opp_score, our_idx))
        else:
            losses.append((ep_id, our_score, opp_score, our_idx))
    except Exception as e:
        print(f"{fname}: ERROR {e}")

print(f"\n=== SUMMARY: {len(wins)} wins, {len(losses)} losses ===")
print(f"Win rate: {len(wins)/(len(wins)+len(losses)):.1%}")
print(f"Our mean score: {sum(s for _,s,_,_ in wins+losses)/len(wins+losses):.0f}")
print(f"Opp mean score: {sum(s for _,_,s,_ in wins+losses)/len(wins+losses):.0f}")
