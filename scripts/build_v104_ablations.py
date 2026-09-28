import os
import re

def build_ablations():
    source_file = 'e:/Setup/kaggle/kaggriculture/submission_v104_quote_priority.py'
    out_dir = 'e:/Setup/kaggle/kaggriculture/agents/ablations'
    os.makedirs(out_dir, exist_ok=True)
    
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # B: No quote priority (replace the sorted call)
    cont_b = re.sub(r'def _r37_quote_priority\(.*?\):', 'def _r37_quote_priority(observation, order, stock):\n    return 0\ndef _r37_quote_priority_old(observation, order, stock):', content)
    with open(os.path.join(out_dir, 'v104_minus_b_quote_priority.py'), 'w', encoding='utf-8') as f:
        f.write(cont_b)

    # C: No care gating
    cont_c = content.replace("vt_skipped_care", "dummy_care")
    with open(os.path.join(out_dir, 'v104_minus_c_care_gating.py'), 'w', encoding='utf-8') as f:
        f.write(cont_c)
        
    # D: No CTRTABLE
    cont_d = re.sub(r'CTRTABLE\s*=\s*\[.*?\]', 'CTRTABLE = []', content, flags=re.DOTALL)
    with open(os.path.join(out_dir, 'v104_minus_d_ctrtable.py'), 'w', encoding='utf-8') as f:
        f.write(cont_d)
        
    # E: No terminal liquidation
    cont_e = content.replace('== 719', '== 9999').replace('==719', '==9999')
    with open(os.path.join(out_dir, 'v104_minus_e_terminal.py'), 'w', encoding='utf-8') as f:
        f.write(cont_e)
        
    # F: No reflex layers
    # We truncate the file before the reflex layers are added. 
    # Usually they are at the end. We'll search for "# Claude CARROT2 layer" or "# v9 CARROT:" 
    # Wait, the task mentioned CARROT and SHEDROOM. Let's see if we can find the point where `_V9_CARROT = {}` is defined and truncate there, but wait!
    # A cleaner way is to disable the layers in the `agent` wrapper.
    # Let's just find the original base agent and rename it to `agent`.
    
    print("Ablation agents built.")

if __name__ == '__main__':
    build_ablations()
