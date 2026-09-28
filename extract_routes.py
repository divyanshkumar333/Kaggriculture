import json
import ast

def find_dict(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.dump(node.value)
    return None

def extract():
    with open('submission_v104_quote_priority.py', 'r', encoding='utf-8') as f:
        src = f.read()
    print('R108_DATA:', find_dict(src, '_R108_DATA')[:200])
    print('V92_TABLE:', find_dict(src, '_V92_TABLE')[:200])
    
if __name__ == '__main__':
    extract()
