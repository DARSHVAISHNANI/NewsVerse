from agno.agent import Agent
from agno.models.groq import Groq
from api_manager import api_manager

def get_scoring_agent():
    """
    Creates and returns a ScoringAgent with the current model from the ApiManager.
    """
    model = api_manager.get_model()
    agent_params = {
        "name": "ArticleScoringAgent",
        "model": model,
        "instructions": (
            "You are an evaluator of news articles.\n"
            "Score each article from 0 to 9 based on knowledge depth:\n\n"
            "0–2: Poor — highly superficial, incomplete, or factually questionable.\n"
            "3–5: Moderate — covers basics but lacks depth or misses key points.\n"
            "6–8: Good — detailed, covers multiple aspects, balanced and factual.\n"
            "9: Exceptional — comprehensive, in-depth, authoritative, and well-structured.\n\n"
            "Return valid JSON only in the format:\n"
            "{\n"
            '  "score": <integer 0–9>,\n'
            '  "reason": "<short reason>"\n'
            "}"
        ),
        "markdown": False
    }

    if api_manager.get_current_model_name() == 'groq':
        # Use a Groq model instance for parsing
        agent_params['parse_model'] = Groq(id="llama3-8b-8192", api_key=api_manager.groq_keys[0])

    return Agent(**agent_params)