# in article_scorer/utils.py

import json
import os
import re

def parseScoreJson(text: str) -> dict | None:
    """
    Repairs and parses a raw string that should contain JSON for the score.
    Returns a dictionary if successful, otherwise None.
    """
    print(f"DEBUG: Raw input to parser:\n---\n{text[:200]}...\n---") # Added debug print
    
    if not isinstance(text, str):
        print("Error: Input to parser is not a string.")
        return None

    # 1. Aggressive Isolation: Find the outermost JSON object
    # This strips away markdown blocks (```json...```) and surrounding text
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    
    if not json_match:
        print(f"⚠️  Could not find JSON object in response.")
        return None
        
    cleaned_str = json_match.group(0)

    # 2. Cleanup: Escape inner quotes in the 'reason' field
    try:
        def escape_quotes_in_reason(match):
            # Group 1: '"reason": "'
            key_part = match.group(1) 
            # Group 2: The content of the reason string
            reason_text = match.group(2)
            # Group 3: The closing quote '"'
            closing_quote = match.group(3) 
            
            # Escape all double quotes within the explanation text
            escaped_text = reason_text.replace('"', '\\"')
            
            # Reconstruct the key-value pair
            return f'{key_part}{escaped_text}{closing_quote}' 

        # Safely targets the content of the "reason" value.
        cleaned_str = re.sub(
            r'("reason"\s*:\s*")(.*?)(")',
            escape_quotes_in_reason,
            cleaned_str,
            flags=re.DOTALL
        )
        
        # Remove trailing commas before a closing brace (a common LLM JSON error)
        cleaned_str = re.sub(r",\s*([}\]])", r"\1", cleaned_str)

        # 3. Attempt to Parse
        result = json.loads(cleaned_str)
        
        # 4. Validation: Ensure required keys exist and cast score to int
        if "score" in result and "reason" in result:
            # Explicitly cast score to int to handle cases where LLM quotes it (e.g. "9")
            try:
                result["score"] = int(result["score"])
            except ValueError:
                print(f"⚠️ 'score' value is not a valid integer: {result.get('score')}")
                return None
            
            return result
        else:
            print(f"⚠️  Parsed JSON is missing required keys: {result}")
            return None

    except json.JSONDecodeError as e:
        print(f"⚠️  Could not parse JSON from response: {e}")
        print(f"DEBUG: Problematic cleaned string:\n---\n{cleaned_str}\n---")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during score JSON parsing: {e}")
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