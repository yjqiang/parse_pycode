import json
from typing import Any


def save_json(path: str, data: Any) -> None:
    with open(path, 'w+', encoding='utf8') as f:
        f.write(json.dumps(data, indent=4))


def open_json(path: str) -> Any:
    with open(path, encoding='utf8') as f:
        return json.load(f)
