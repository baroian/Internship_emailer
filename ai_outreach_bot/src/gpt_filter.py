from __future__ import annotations

import json
from typing import List

from openai import OpenAI

SYSTEM_PROMPT = 'You are an expert curator. Given a lab name and a JSON array of candidate researchers, return ONLY those whose PRIMARY research is large-language models. Exclude peripheral NLP or CV. Respond with JSON: [{"name":"", "reason":"", "confidence":0-1}].'


def filter_candidates(lab_name: str, raw_json: List[dict]) -> List[dict]:
    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Lab: {lab_name}\nRaw candidates: {raw_json}"},
        ],
        temperature=0,
    )
    content = resp.choices[0].message.content or "[]"
    return json.loads(content)
