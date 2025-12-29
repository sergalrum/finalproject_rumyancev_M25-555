import json
from pathlib import Path


DATA_DIR = Path("data")

def load_json(filename: str) -> dict:
    """Загружает JSON‑файл из data/."""
    path = DATA_DIR / filename
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(filename: str, data: dict):
    """Сохраняет данные в JSON‑файл."""
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
