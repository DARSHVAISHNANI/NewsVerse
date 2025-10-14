# backend/Recommendation_Engine/agents.py
from agno.agent import Agent
from agno.models.groq import Groq  # Import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.webbrowser import WebBrowserTools
from api_manager import api_manager

def get_analysis_agent():
    """
    Creates and returns a UserPreferenceAnalysisAgent with the current model.
    """
    model = api_manager.get_model()
    agent_params = {
        "name": "UserPreferenceAnalysisAgent",
        "model": model,
        "instructions": (
            "You are an expert user behavior analyst specializing in news consumption patterns. "
            "Base most of your analysis on NER entities (persons, organizations, locations). "
            "Use keywords only as secondary hints. Provide a detailed, paragraph-style summary of the user's interests."
        ),
        "tools": [DuckDuckGoTools(), WebBrowserTools()],
        "add_history_to_context": False,
        "markdown": True
    }
    # No parser_model needed here as the output is a paragraph, not structured JSON.
    return Agent(**agent_params)

def get_article_match_agent():
    """
    Creates and returns an ArticleRecommenderAgent with the current model.
    """
    model = api_manager.get_model()
    agent_params = {
        "name": "ArticleRecommenderAgent",
        "model": model,
        "instructions": (
            "You are an expert news recommendation engine. "
            "You will receive a user preference summary and a shortlist of news articles. "
            "Rank the top 10 articles in order of relevance and return ONLY their `_id`s in a JSON list."
        ),
        "add_history_to_context": False,
        "markdown": True
    }

    if api_manager.get_current_model_name() == 'groq':
        # Use a Groq model instance for parsing
        agent_params['parser_model'] = Groq(id="openai/gpt-oss-120b", api_key=api_manager.groq_keys[0])

    return Agent(**agent_params)