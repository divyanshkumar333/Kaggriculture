import sys
import random
from fast_tournament import run_fast_tournament

if __name__ == '__main__':
    # 50 random seeds
    random.seed(1337)
    seeds = [random.randint(1, 999999) for _ in range(50)]

    cand = r"e:\Setup\kaggle\kaggriculture\agents\v116_carrot_margin_optimized.py"
    pop = [r"e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py"]

    run_fast_tournament(cand, pop, seeds=seeds, max_workers=6)
