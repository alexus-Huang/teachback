import json
from llm import ask


def _parse_json(raw):
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


def get_key_concepts(topic, n=6, level="middle school"):
    prompt = f"""List the {n} most important ideas a {level} student must understand to truly grasp "{topic}".
Rules:
- Each idea is ONE plain, simple sentence of 6-14 words.
- Use everyday words a student would actually say. No jargon or fancy phrasing.
- Be concrete: say what happens and why, not abstract principles.
- Cover different aspects. Don't repeat yourself.
- Include at least one idea about how two parts connect.
Return ONLY a JSON array of strings. No other text."""

    data = _parse_json(ask([{"role": "user", "content": prompt}], temperature=0.3))
    return [str(c) for c in data][:n]


def get_concept_links(topic, n=8):
    prompt = f"""Build a concept map of "{topic}" as {n} links between ideas.
Rules:
- Each link has "from" and "to" (each a key term of 1-3 words) and "relation" (a short verb phrase of 1-4 words).
- Together the links should form one connected map.
- Spell each term identically every time it appears.
Return ONLY a JSON array like [{{"from": "...", "relation": "...", "to": "..."}}]. No other text."""

    data = _parse_json(ask([{"role": "user", "content": prompt}], temperature=0.3))
    links = []
    for item in data:
        if isinstance(item, dict) and all(k in item for k in ("from", "relation", "to")):
            links.append({k: str(item[k]) for k in ("from", "relation", "to")})
    return links[:n]