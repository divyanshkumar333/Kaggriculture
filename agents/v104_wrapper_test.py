import sys, os, importlib.util
sys.path.insert(0, os.path.dirname(__file__))
v104_path = os.path.join(os.path.dirname(__file__), 'v104_quote_priority.py')
spec = importlib.util.spec_from_file_location('m', v104_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def agent(obs, cfg=None):
    return mod.agent(obs, cfg)
