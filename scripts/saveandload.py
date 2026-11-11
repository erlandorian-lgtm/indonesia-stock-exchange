import json
from pathlib import Path

def load_json_list(path):
    path = Path(path)
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp.replace(path)