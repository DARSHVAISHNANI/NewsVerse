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
            "Step 3: Use ONLY ONE search (DuckDuckGo, GoogleSearch, WebBrowser, or WebsiteTools) for that claim.",
            "Step 4: Compare the claim to the top 3 reputable search results (BBC, Reuters, AP, Bloomberg, etc.).",
            "Step 5: Decide if the claim is factually correct (true or false).",
            # **FIX: Use extremely strict instructions for JSON output**
            "Step 6: Output the result ONLY in a raw JSON object (no markdown block or surrounding text). The JSON MUST have exactly two fields: 'llm_verdict' (boolean: true/false) and 'fact_check_explanation' (string: short reason).",
            'Example: {"llm_verdict": true, "fact_check_explanation": "The claim is supported by multiple reputable sources."}'
        ],
        "tools": [DuckDuckGoTools(), GoogleSearchTools(), WebBrowserTools(), WebsiteTools()],
        "markdown": False
        # The 'response_schema' parameter is removed as it caused the error.
    }

    if api_manager.get_current_model_name() == 'groq':
        # Use a Groq model instance for parsing
        agent_params['parser_model'] = Groq(id="openai/gpt-oss-120b", api_key=api_manager.groq_keys[0])

    return Agent(**agent_params)