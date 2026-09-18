from kaggle_environments import make

agents = {
    'v094_a': 'agents/v094_hybrid_a.py',
    'v094_b': 'agents/v094_hybrid_b.py',
    'v094_c': 'agents/v094_hybrid_c.py',
    '013':    'agents/013_robust_trace.py',
    '014':    'agents/014_robust_trace.py',
}
opps = [
    ('v057', 'agents/v057_generalized_spoiler.py'),
    ('rand', 'random'),
]

for a_name, a_path in agents.items():
    scores = []
    for o_name, o_path in opps:
        for seat in range(2):
            if seat == 0:
                p1, p2 = a_path, o_path
            else:
                p1, p2 = o_path, a_path
            env = make('kaggriculture', configuration={'episodeSteps': 720}, debug=False)
            env.run([p1, p2])
            f = env.steps[-1]
            our = f[0].reward if seat == 0 else f[1].reward
            scores.append(our)
    print(f'{a_name}: mean={sum(scores)/len(scores):.0f} min={min(scores):.0f} scores={["{:.0f}".format(s) for s in scores]}')
