import os
import sys
sys.path.insert(0, os.path.abspath("."))
from kaggle_environments import make
from scripts.tournament_population import load_agent

def test_yarn_override():
    base_file = r"e:\Setup\kaggle\kaggriculture\agents\the_2945_farm.py"
    with open(base_file, "r", encoding="utf-8") as f:
        code_base = f.read()
        
    # Variant without the forced _V92_TABLE override (lets _R108_SHOP_ROUTES choose)
    code_no_v92 = code_base.replace(
        "state['route']=_V92_TABLE.get(shops,state['route'])",
        "# state['route']=_V92_TABLE.get(shops,state['route'])"
    )
    
    # Save variant to agents/v103_no_yarn_clamp.py
    var_file = r"e:\Setup\kaggle\kaggriculture\agents\v103_no_yarn_clamp.py"
    with open(var_file, "w", encoding="utf-8") as f:
        f.write(code_no_v92)
    print("Saved v103_no_yarn_clamp.py")

if __name__ == "__main__":
    test_yarn_override()
