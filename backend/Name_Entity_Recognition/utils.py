# in ner_processor/utils.py

import json
import re

def parseJsonOutput(raw_text: str) -> dict | None:
    """
    Cleans and parses a raw string that should contain JSON.
    Returns a dictionary if successful, otherwise None.
    """
    if not isinstance(raw_text, str):
        return None

    try:
        # Clean output: remove possible code fences and whitespace
        cleaned = re.sub(r"^`{3,}[a-zA-Z]*\n?", "", raw_text.strip())
        cleaned = re.sub(r"\n?`{3,}$", "", cleaned)
        cleaned = cleaned.strip()

        # Defensive check: must start and end with braces for JSON
        if not cleaned.startswith("{") or not cleaned.endswith("}"):
             print(f"❗ NER output not valid JSON format:\n{cleaned}")
             return None

        return json.loads(cleaned)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"❌ JSON decode error: {e}\nOutput:\n{cleaned}")
        return None