# backend/Name_Entity_Recognition/agents.py
from agno.agent import Agent
from api_manager import api_manager
from agno.models.groq import Groq  # Import Groq

def get_ner_agent():
    """
    Creates and returns a NerAgent with the current model from the ApiManager.
    """
    model = api_manager.get_model()
    agent_params = {
        "name": "NERGeminiAgent",
        "model": model,
        "instructions": (
            "Extract all unique named entities from the following news article text and categorize them "
            'as "Person", "Location" (including cities/countries/regions), or "Organization" (companies, institutions). '
            "Return strictly a JSON object in this format:\n"
            "{\n"
            '  "Person": [list of unique person names],\n'
            '  "Location": [list of unique locations],\n'
            '  "Organization": [list of unique organizations]\n'
            "}\n"
            "Do not include any other text, comments, or explanations. Return valid JSON only."
        ),
        "markdown": False
    }

    if api_manager.get_current_model_name() == 'groq':
        # Use a Groq model instance for parsing
        agent_params['parse_model'] = Groq(id="llama3-8b-8192", api_key=api_manager.groq_keys[0])

    return Agent(**agent_params)
