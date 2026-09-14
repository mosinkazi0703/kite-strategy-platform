from pathlib import Path
import yaml
def load_enabled_strategies(directory="config"):
    result=[]
    for path in sorted(Path(directory).glob("strategy_*.yaml")):
        data=yaml.safe_load(path.read_text(encoding="utf-8")) or {}; data["_path"]=str(path); data["enabled"]=data.get("enabled",True); result.append(data)
    if not result: raise ValueError("no strategy_*.yaml files found")
    return result
