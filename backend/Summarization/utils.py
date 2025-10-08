import re

def CleanJsonOutput(text: str) -> str:
    """
    Cleans the raw output from a model to extract a clean JSON string.
    """
    text = text.strip()
    # Removes markdown code blocks ```json ... ```
    text = re.sub(r"^```json\s*|\s*```$", "", text, flags=re.MULTILINE)
    return text.strip()