# backend/Summarization/agents.py
from agno.agent import Agent
from agno.models.groq import Groq
from api_manager import api_manager


def get_summarization_agent():
    """
    Creates and returns a SummarizationAgent, always using Groq.
    """
    # This agent always uses Groq for summarization tasks.
    # It gets its key from the central api_manager.
    groq_api_key = api_manager.groq_keys[0] if api_manager.groq_keys else None
    model = Groq(id="llama3-8b-8192", api_key=groq_api_key)
    
    return Agent(
        name="Summarization Agent",
        description="Summarize news articles into concise, clear summaries.",
        instructions="""
    You are a news article summarizer. Summarize the given article text in 2-4 sentences.

    Return JSON in this exact format:
    {
        "summary": "<short, concise summary of the article>"
    }

    Do NOT include anything outside the JSON object.
    """,
        model=model,
        debug_mode=True,
        # Use a Groq model instance for parsing to ensure consistent JSON output
        parse_model=Groq(id="llama3-8b-8192", api_key=groq_api_key)
    )


def get_story_agent():
    """
    Creates and returns a StoryAgent, always using Groq.
    """
    groq_api_key = api_manager.groq_keys[0] if api_manager.groq_keys else None
    model = Groq(id="llama3-8b-8192", api_key=groq_api_key)
    
    return Agent(
        name="Storytelling Summarizer",
        description="Summarize news articles in a fun, simple story-like way for children.",
        instructions="""You are a children's story writer. Read the article carefully and summarize it in a fun, simple, and easy-to-read way for kids.

    Rules:
    1. Use simple language suitable for 6-12 year old children.
    2. Make it engaging like a short story.
    3. Keep the summary concise (3-5 sentences max).
    4. Focus on the main events or important points, but avoid technical jargon.
    5. Return JSON in this exact format:

    {
        "story_summary": "<summary written as a story for kids>"
    }

    6. Do NOT include anything outside the JSON object.""",
        model=model,
        debug_mode=True,
        # Use a Groq model instance for parsing to ensure consistent JSON output
        parse_model=Groq(id="llama3-8b-8192", api_key=groq_api_key)
    )