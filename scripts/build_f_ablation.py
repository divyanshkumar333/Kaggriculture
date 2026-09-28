import os

def build_ablations():
    source_file = 'e:/Setup/kaggle/kaggriculture/submission_v104_quote_priority.py'
    out_dir = 'e:/Setup/kaggle/kaggriculture/agents/ablations'
    
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the line 'agent=globals().pop(\'agent\')' near line 2892 and cut it off there
    cutoff = -1
    for i, line in enumerate(lines):
        if "v9 COURIER" in line:
            cutoff = i - 1
            break
            
    if cutoff != -1:
        cont_f = "".join(lines[:cutoff])
        with open(os.path.join(out_dir, 'v104_minus_f_reflex_layers.py'), 'w', encoding='utf-8') as f:
            f.write(cont_f)
        print(f"Created F, truncated at {cutoff}")
    else:
        print("Could not find cutoff for F.")

if __name__ == '__main__':
    build_ablations()
