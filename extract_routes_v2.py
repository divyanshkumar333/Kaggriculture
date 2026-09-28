import json
import zlib
import base64
import re
import ast

def extract():
    with open('submission_v104_quote_priority.py', 'r', encoding='utf-8') as f:
        src = f.read()
    
    # Try finding the base85 string directly from _R108_DATA assignment
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '_R108_DATA':
                    # Extract the b85 string from AST
                    # Node is Call(func=Attribute(value=Name(id='json'), attr='loads'), args=[Call(...)])
                    try:
                        b85_str = node.value.args[0].args[0].args[0].value
                        data = json.loads(zlib.decompress(base64.b85decode(b85_str)).decode('utf-8'))
                        print("Routes found:", list(data['routes'].keys()))
                        # print the lengths of these routes
                        for k, v in data['routes'].items():
                            print(f"Route {k}: {len(v)} steps")
                    except Exception as e:
                        print("Failed to extract _R108_DATA:", e)

    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '_V92_TABLE':
                    print("V92 Routes:", set([k.value for k in node.value.values]))
                if isinstance(target, ast.Name) and target.id == '_V93_ROUTE_BY_RIVAL':
                    print("V93 Routes:", set([k.value for k in node.value.values]))

if __name__ == '__main__':
    extract()
