# backend/Sentiment_Analysis/agents.py
from agno.agent import Agent
from agno.models.groq import Groq  # Import Groq
from api_manager import api_manager

def get_sentiment_agent():
    """
    Creates and returns a SentimentAgent with the current model from the ApiManager.
    """
    model = api_manager.get_model()
    agent_params = {
        "name": "Sentiment Agent",
        "description": "Analyze the content of news articles and determine their sentiment.",
        "instructions": """
        You are a sentiment evaluation agent. Analyze the tone and language of the article text.  
    Determine sentiment strictly as **Positive, Negative, or Neutral** based on these rules:

    1. **Positive** → The article contains positive keywords (e.g., growth, profit, gain, recovery, expansion, strong, successful), or the overall tone is optimistic and confidence-building.  
    2. **Negative** → The article contains negative keywords (e.g., loss, decline, fall, risk, weak, downgrade, failure), or the overall tone is pessimistic, warning, or confidence-reducing.  
    3. **Neutral** → The article is mainly factual, descriptive, or balanced — with no clear positive or negative tone. Includes objective reporting, announcements, or mixed signals.  
    4. Return only JSON in this exact format:

    {
        "sentiment": "<Positive|Negative|Neutral>",
        "reason": "<short reason explaining the classification>"
    }

    5. Reason should be brief (1-2 sentences).  
    6. Do NOT include anything outside the JSON object.

    Input: The article text will be provided. Analyze carefully and return ONLY the JSON object.
        """,
        "model": model,
        "debug_mode": True,
    }

    if api_manager.get_current_model_name() == 'groq':
        # Use a Groq model instance for parsing
        agent_params['parser_model'] = Groq(id="openai/gpt-oss-120b", api_key=api_manager.groq_keys[0])

    return Agent(**agent_params)