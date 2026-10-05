import json
from llm import ask

def get_key_concepts(topic, n=6):
    prompt = f"""List the {n} most important ideas someone must understand to truly grasp "{topic}".
Rules:
- Each idea is ONE complete sentence, under 20 words.
- Focus on how and why, not just definitions.
- Include at least one idea about how two parts connect.
Return ONLY a JSON array of strings. No other text."""

    raw = ask([{"role": "user", "content": prompt}], temperature=0.3)
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        concepts = json.loads(raw)
        return [str(c) for c in concepts][:n]
    except json.JSONDecodeError:
        return []