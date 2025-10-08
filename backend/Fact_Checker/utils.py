# in fact_checker/utils.py

import json
import re

def parseJsonOutput(raw_text: str) -> dict | None:
    """
    Cleans and parses a raw string that should contain JSON.
    Returns a dictionary if successful, otherwise None.
    """
    if not isinstance(raw_text, str):
        # If the input is already a dict, return it directly
        return raw_text if isinstance(raw_text, dict) else None

    try:
        # Clean markdown code blocks like ```json ... ```
        clean_str = re.sub(r"^```[a-zA-Z]*\n?", "", raw_text.strip())
        clean_str = re.sub(r"\n?```$", "", clean_str.strip())

        # Parse the cleaned string into a dictionary
        return json.loads(clean_str)
    except (json.JSONDecodeError, TypeError):
        print(f"⚠️  Could not parse JSON from response: '{raw_text[:100]}...'")
        return None