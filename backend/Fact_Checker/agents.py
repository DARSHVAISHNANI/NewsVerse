# backend/Fact_Checker/agents.py
from agno.agent import Agent
from agno.models.groq import Groq  # Import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.webbrowser import WebBrowserTools
from agno.tools.website import WebsiteTools
from api_manager import api_manager

def get_fact_checker_agent():
    """
    Creates and returns a FactCheckerAgent with the current model from the ApiManager.
    """
    model = api_manager.get_model()
    agent_params = {
        "name": "FactCheckerAgent",
        "model": model,
        "description": "Fact-check an article by extracting its main factual claim and verifying it with a single web search.",
        "instructions": [
            "Step 1: Read the provided news article text.",
            "Step 2: Extract the main factual claim from the article.",
            "Step 3: Use ONLY ONE search for that claim.",
            "Step 4: Compare the claim to the top 3 reputable search results.",
            "Step 5: Decide if the claim is factually correct.",
            "Step 6: Output ONLY in JSON format with fields: llm_verdict (true or false), fact_check_explanation (short reason)."
        ],
        "tools": [DuckDuckGoTools(), GoogleSearchTools(), WebBrowserTools(), WebsiteTools()],
        "markdown": False
    }

    if api_manager.get_current_model_name() == 'groq':
        # Use a Groq model instance for parsing
        agent_params['parse_model'] = Groq(id="llama3-8b-8192", api_key=api_manager.groq_keys[0])

    return Agent(**agent_params)