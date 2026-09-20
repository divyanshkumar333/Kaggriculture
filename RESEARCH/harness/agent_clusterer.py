import os
import glob
import re
import base64
import zlib
import json
import hashlib

def get_action_hash(actions, end_idx=None):
    if not actions: return "none"
    sliced = actions[:end_idx] if end_idx else actions
    return hashlib.md5(json.dumps(sliced, sort_keys=True).encode()).hexdigest()[:8]

def extract_trace(code):
    match = re.search(r"base64\.b85decode\(\s*[\"'](.*?)[\"']", code, re.DOTALL)
    if not match:
        match = re.search(r"base64\.b64decode\(\s*[\"'](.*?)[\"']", code, re.DOTALL)
    if not match:
        return None
    try:
        b64_str = match.group(1).replace('\n', '').replace('\r', '')
        # Try b85 first, then b64
        try:
            decompressed = zlib.decompress(base64.b85decode(b64_str))
        except:
            decompressed = zlib.decompress(base64.b64decode(b64_str))
        return json.loads(decompressed.decode("utf-8"))
    except Exception as e:
        return None

def extract_engine_hash(code):
    # Remove the base64 string to just hash the logic
    cleaned = re.sub(r"base64\.[bB]\d+decode\(\s*[\"'].*?[\"']\s*\)", "REMOVED_TRACE", code, flags=re.DOTALL)
    return hashlib.md5(cleaned.encode()).hexdigest()[:8]

def main():
    agents_dir = "agents"
    agent_files = glob.glob(os.path.join(agents_dir, "*.py"))
    agent_files.append("main.py")
    
    out_lines = ["agent,shared_engine_hash,trace_hash,trace_prefix_hash_24,trace_prefix_hash_72,trace_prefix_hash_144,trace_prefix_hash_200,trace_prefix_hash_400,trace_suffix_hash"]
    
    for af in sorted(agent_files):
        with open(af, "r", encoding="utf-8") as f:
            code = f.read()
            
        actions = extract_trace(code)
        engine_hash = extract_engine_hash(code)
        
        name = os.path.basename(af)
        if actions:
            t_hash = get_action_hash(actions)
            t24 = get_action_hash(actions, 24)
            t72 = get_action_hash(actions, 72)
            t144 = get_action_hash(actions, 144)
            t200 = get_action_hash(actions, 200)
            t400 = get_action_hash(actions, 400)
            tsuffix = get_action_hash(actions[400:]) if len(actions) > 400 else "none"
            
            out_lines.append(f"{name},{engine_hash},{t_hash},{t24},{t72},{t144},{t200},{t400},{tsuffix}")
        else:
            out_lines.append(f"{name},{engine_hash},dynamic,dynamic,dynamic,dynamic,dynamic,dynamic,dynamic")
            
    with open("RESEARCH/agent_lineage_clusters.csv", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
        
if __name__ == "__main__":
    main()
