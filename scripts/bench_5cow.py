from kaggle_environments import make

# Test the extracted 5-COW opponent vs our best agents
tests = [
    ('v095_5cow(P0) vs v057', 'agents/v095_5cow_opening.py', 'agents/v057_generalized_spoiler.py'),
    ('v057(P0) vs v095_5cow(P1)', 'agents/v057_generalized_spoiler.py', 'agents/v095_5cow_opening.py'),
    ('v095_5cow(P0) vs 013', 'agents/v095_5cow_opening.py', 'agents/013_robust_trace.py'),
    ('013(P0) vs v095_5cow(P1)', 'agents/013_robust_trace.py', 'agents/v095_5cow_opening.py'),
    ('v095_5cow(P0) vs 014', 'agents/v095_5cow_opening.py', 'agents/014_robust_trace.py'),
    ('014(P0) vs v095_5cow(P1)', 'agents/014_robust_trace.py', 'agents/v095_5cow_opening.py'),
    ('v095_5cow(P0) vs v092b', 'agents/v095_5cow_opening.py', 'agents/v092b_replay_seed.py'),
    ('v095_5cow vs rand', 'agents/v095_5cow_opening.py', 'random'),
]

for label, a1, a2 in tests:
    env = make('kaggriculture', configuration={'episodeSteps': 720}, debug=False)
    env.run([a1, a2])
    f = env.steps[-1]
    p0, p1 = f[0].reward, f[1].reward
    winner = 'P0' if p0 > p1 else 'P1'
    print(f'{label}: P0={p0:.0f} P1={p1:.0f} [{winner} wins]')
