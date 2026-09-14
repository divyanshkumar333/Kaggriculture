import os
import sys
import subprocess
import json

DEPTHS = [0, 1, 4, 8, 12, 18, 24, 30]
TEMPLATE_AGENT = "agents/v052_v16_adaptive.py"
OPPONENT = "agents/public_v16_rc5.py"
MATCHES = 200 # Faster sweep, 100 pairs

def generate_agent(depth):
    agent_path = f"agents/tmp_v052_depth_{depth}.py"
    with open(TEMPLATE_AGENT, "r") as f:
        content = f.read()
    
    # Replace the fallback depth
    content = content.replace(
        'max_lookahead = 1 if state.get("is_v16", False) else 30',
        f'max_lookahead = {depth} if state.get("is_v16", False) else 30'
    )
    
    with open(agent_path, "w") as f:
        f.write(content)
    return agent_path

def run_match(agent_path, depth):
    print(f"\\n--- Running Sweep for Fallback Depth {depth} ---")
    
    cmd = [
        os.path.join(".venv", "Scripts", "python.exe"),
        "scripts/tournament_harness.py",
        agent_path,
        OPPONENT,
        str(MATCHES // 2),
        f"V052_Fallback_D{depth}",
        "V16_Public"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running matches for Depth {depth}:\\n{result.stderr}")
    else:
        print(f"Depth {depth} completed successfully.")

def main():
    for depth in DEPTHS:
        agent_path = generate_agent(depth)
        run_match(agent_path, depth)

if __name__ == "__main__":
    main()
