import re

def CleanJsonOutput(text: str) -> str:
    """Remove Markdown code fences and extra whitespace from LLM output."""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()
