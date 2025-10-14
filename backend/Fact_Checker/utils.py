import json
import re

def parseJsonOutput(llm_output_str: str):
    """
    Parses the LLM's JSON output, cleaning it up as much as possible.
    Handles common LLM formatting errors, including unescaped double quotes within string values.
    """
    print(f"DEBUG: Raw LLM output received:\n---\n{llm_output_str}\n---")

    if not llm_output_str or not llm_output_str.strip():
        print("Error: LLM output is empty or contains only whitespace.")
        return None

    # --- 1. Basic Cleaning: Isolate the JSON object ---
    json_match = re.search(r"\{.*\}", llm_output_str, re.DOTALL)
    if json_match:
        cleaned_str = json_match.group(0)
    else:
        # Fallback to simple stripping if no braces are found
        cleaned_str = re.sub(r"^```json\s*|\s*```$", "", llm_output_str.strip())

    if not cleaned_str.strip():
        print("Error: LLM output was empty after cleaning code blocks.")
        return None

    # --- 2. Advanced Regex-based Corrections (MOVED OUTSIDE TRY BLOCK) ---
    try:
        # Function to escape inner quotes in the explanation text
        def escape_quotes_in_explanation(match):
            key_part = match.group(1)
            explanation_text = match.group(2)
            closing_quote = match.group(3)
            
            # Escape all double quotes within the explanation text
            escaped_text = explanation_text.replace('"', '\\"')
            # Reconstruct the key-value pair
            return f'{key_part}{escaped_text}{closing_quote}' 

        # Apply quote escaping correction to the entire string
        cleaned_str_corrected = re.sub( # <--- DEFINED HERE, BEFORE JSON.LOADS
            r'("fact_check_explanation"\s*:\s*")(.*?)(")',
            escape_quotes_in_explanation,
            cleaned_str,
            flags=re.DOTALL
        )
        
        # Correct single quotes to double quotes and remove trailing commas
        cleaned_str_corrected = re.sub(r"\'", "\"", cleaned_str_corrected)
        cleaned_str_corrected = re.sub(r",\s*([}\]])", r"\1", cleaned_str_corrected)


        # --- 3. Attempt to Parse ---
        return json.loads(cleaned_str_corrected)

    except json.JSONDecodeError as e:
        # Now 'cleaned_str_corrected' is defined here!
        print(f"Error decoding JSON after cleaning: {e}")
        print(f"DEBUG: Problematic cleaned string:\n---\n{cleaned_str_corrected}\n---")
        
        # --- 4. Fallback to Manual Extraction ---
        try:
            print("Attempting manual extraction as a fallback...")
            
            # Relaxed regex for verdict: look for the key and capture the next true/false value
            verdict_match = re.search(r'\"llm_verdict\"\s*:\s*\"?([Tt]rue|[Ff]alse)\"?', cleaned_str_corrected, re.DOTALL)

            # Relaxed regex for explanation: capture content up to the closing quote followed by a brace or end of string.
            explanation_match = re.search(r'\"fact_check_explanation\"\s*:\s*\"(.*?)\"[\}]', cleaned_str_corrected, re.DOTALL)
            
            if verdict_match and explanation_match:
                verdict_str = verdict_match.group(1)
                explanation_str = explanation_match.group(1)
                
                result = {
                    "llm_verdict": True if verdict_str.lower() == 'true' else False,
                    "fact_check_explanation": explanation_str.strip().replace('\\"', '"')
                }
                
                print(f"Successfully extracted manually: {result}")
                return result
            else:
                print("Manual extraction failed to find required fields. Verdict or Explanation missing.")
                return None
        except Exception as manual_e:
            print(f"An error occurred during manual extraction: {manual_e}")
            # Use the most basic string for final failure logging
            print(f"DEBUG: Manual extraction failed on final string:\n---\n{cleaned_str_corrected}\n---") 
            return None

    except Exception as e:
        print(f"An unexpected error occurred during JSON parsing: {e}")
        return None