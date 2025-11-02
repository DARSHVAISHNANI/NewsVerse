# in ner_processor/utils.py

import json
import re
import logging

logger = logging.getLogger("NERPipeline.utils")

def parseJsonOutput(raw_text: str) -> dict | None:
    """
    Cleans and parses a raw string that should contain JSON.
    Returns a dictionary if successful, otherwise None.
    """
    if not isinstance(raw_text, str):
        logger.warning("parseJsonOutput received non-string input")
        return None

    if not raw_text or not raw_text.strip():
        logger.warning("parseJsonOutput received empty input")
        return None

    try:
        # Clean output: remove possible code fences and whitespace
        cleaned = re.sub(r"^`{3,}[a-zA-Z]*\n?", "", raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\n?`{3,}$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        # Try to find JSON object if it's embedded in text
        # Look for the first { and last } that might contain valid JSON
        first_brace = cleaned.find('{')
        last_brace = cleaned.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            cleaned = cleaned[first_brace:last_brace + 1]

        # Defensive check: must start and end with braces for JSON
        if not cleaned.startswith("{") or not cleaned.endswith("}"):
            logger.warning(f"❗ NER output not valid JSON format (missing braces)")
            logger.debug(f"   First 200 chars: {cleaned[:200]}")
            return None

        parsed = json.loads(cleaned)
        
        # Validate the structure
        if not isinstance(parsed, dict):
            logger.warning(f"❗ Parsed JSON is not a dictionary")
            return None
            
        # Check for expected keys
        expected_keys = ["Person", "Location", "Organization"]
        for key in expected_keys:
            if key not in parsed:
                logger.debug(f"   Missing key '{key}' in parsed JSON, adding empty list")
                parsed[key] = []
            elif not isinstance(parsed[key], list):
                logger.warning(f"   Key '{key}' is not a list, converting...")
                parsed[key] = [parsed[key]] if parsed[key] else []
        
        return parsed
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error: {e}")
        logger.debug(f"   Problematic output (first 500 chars):\n{cleaned[:500]}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error parsing JSON: {e}", exc_info=True)
        logger.debug(f"   Raw output (first 500 chars):\n{raw_text[:500]}")
        return None