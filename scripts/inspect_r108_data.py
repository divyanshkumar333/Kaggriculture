"""Decompress and inspect the _R108_DATA route table in the 2945 farm."""
import json, zlib, base64, re

with open(r'e:\Setup\kaggle\kaggriculture\agents\v104_quote_priority.py', encoding='utf-8') as f:
    content = f.read()

# Extract the b85decode data blob
idx = content.find("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
if idx < 0:
    idx = content.find('_R108_DATA=json.loads(zlib.decompress(base64.b85decode(')
    print(f"Found alternate at {idx}")
    print(content[idx:idx+300])
else:
    print(f"Found at {idx}")
    # Extract the encoded blob
    start = idx + len("_R108_DATA=json.loads(zlib.decompress(base64.b85decode('")
    end = content.index("'", start)
    encoded = content[start:end]
    print(f"Encoded blob length: {len(encoded)} chars")
    
    raw = zlib.decompress(base64.b85decode(encoded))
    data = json.loads(raw)
    
    print(f'\n_R108_DATA keys: {list(data.keys())}')
    print(f'Decompressed size: {len(raw)} bytes')
    
    for key in list(data.keys()):
        val = data[key]
        if isinstance(val, list):
            print(f'\n{key}: list of {len(val)} items')
            if val:
                first = val[0]
                print(f'  Type of first item: {type(first).__name__}')
                if isinstance(first, dict):
                    print(f'  First item keys: {list(first.keys())}')
                    print(f'  First item preview: {str(first)[:300]}')
                else:
                    print(f'  First item preview: {str(first)[:200]}')
        elif isinstance(val, dict):
            print(f'\n{key}: dict with {len(val)} keys')
            print(f'  Sample keys: {list(val.keys())[:10]}')
        else:
            print(f'\n{key}: {type(val).__name__} = {str(val)[:100]}')

    # Save decoded data for analysis
    with open(r'e:\Setup\kaggle\kaggriculture\RESEARCH\kaggle_loop\kaggle_forensics\r108_data_structure.json', 'w', encoding='utf-8') as f:
        # Only save metadata, not full action sequences (too large)
        summary = {}
        for key, val in data.items():
            if isinstance(val, list):
                summary[key] = f"list[{len(val)}]"
                if val and isinstance(val[0], dict):
                    summary[key + '_first_keys'] = list(val[0].keys())
            elif isinstance(val, dict):
                summary[key] = f"dict[{len(val)}]"
                summary[key + '_keys'] = list(val.keys())[:20]
            else:
                summary[key] = val
        json.dump(summary, f, indent=2)
    print(f"\nSaved structure summary to r108_data_structure.json")
