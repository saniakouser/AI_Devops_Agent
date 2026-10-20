import json
import re
from pathlib import Path

KB_PATH = Path(__file__).with_name("knowledge_base.json")

def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))

def search_incidents(query: str, limit: int = 3) -> list[dict]:
    try:
        records = json.loads(KB_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    query_tokens = _tokens(query)
    ranked = []
    for item in records:
        corpus = " ".join(str(v) for v in item.values())
        score = len(query_tokens & _tokens(corpus))
        if score:
            ranked.append((score, item))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in ranked[:limit]]
