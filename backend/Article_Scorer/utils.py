# in article_scorer/utils.py

import json
import os
import re

def parseScoreJson(text: str) -> dict | None:
    """
    Repairs and parses a raw string that should contain JSON for the score.
    Returns a dictionary if successful, otherwise None.
    """
    if not isinstance(text, str):
        return None

    try:
        # Basic cleaning of markdown and whitespace
        text = text.strip()
        text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()

        # More advanced repair logic from your original script
        seen = set()
        lines = []
        for line in text.splitlines():
            match = re.match(r'\s*"(\w+)"\s*:', line)
            if match:
                key = match.group(1)
                if key in seen:
                    continue
                seen.add(key)
            lines.append(line)
        repaired_text = "\n".join(lines)
        repaired_text = re.sub(r'"\s*\n\s*"', '",\n"', repaired_text)

        return json.loads(repaired_text)
    except (json.JSONDecodeError, TypeError):
        print(f"⚠️  Could not parse JSON from response: '{text[:100]}...'")
        return None

def saveResultsToJson(results_list: list, filename: str):
    """
    Appends results to a JSON file, creating it if it doesn't exist.
    """
    if not results_list:
        print("ℹ No new results to save.")
        return

    old_data = []
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️  Warning: Could not read existing data from {filename}. It might be corrupted.")
            old_data = []

    # Append new results to the old data
    old_data.extend(results_list)

    # Write the combined data back to the file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(old_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Processed {len(results_list)} grouped articles. Saved to {filename}")