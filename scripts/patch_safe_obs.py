import re
import sys

def patch_file(filepath):
    with open(filepath, 'r') as f:
        code = f.read()

    # The safe observation accessor
    safe_obs_code = """
def _get(value, key, default=None):
    try:
        if isinstance(value, dict):
            return value.get(key, default)
        
        # Kaggle Observation objects have attributes
        if hasattr(value, key):
            val = getattr(value, key)
            if val is not None:
                return val
        
        # Fallback for weird proxy objects
        if hasattr(value, 'get'):
            val = value.get(key)
            if val is not None:
                return val
                
    except Exception:
        pass
        
    return default
"""
    # Replace old _get if it exists
    if "def _get(value, key, default=None):" in code:
        # Find the end of the existing _get
        old_get_start = code.find("def _get(value, key, default=None):")
        old_get_end = code.find("def ", old_get_start + 1)
        if old_get_end == -1:
            old_get_end = len(code)
            
        code = code[:old_get_start] + safe_obs_code.strip() + "\n\n" + code[old_get_end:]
    else:
        # Just put it after imports
        import_end = code.rfind("import ")
        newline = code.find("\n", import_end)
        code = code[:newline+1] + "\n" + safe_obs_code.strip() + "\n\n" + code[newline+1:]

    # Remove the generic catch-all exception in the main agent function that falls back to PASS
    # and replace with loud failure or strict exception handling
    if "except Exception:" in code:
        code = code.replace("except Exception:", "except Exception as e:\n        import traceback; traceback.print_exc()\n        raise e # FAIL LOUDLY")

    # Replace any direct obs.get() calls with _get(obs, )
    code = re.sub(r'obs\.get\((.*?)\)', r'_get(obs, \1)', code)

    with open(filepath, 'w') as f:
        f.write(code)

    print(f"Patched {filepath}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: patch_safe_obs.py <file>")
        sys.exit(1)
    patch_file(sys.argv[1])
