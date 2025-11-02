# backend/Name_Entity_Recognition/agents.py
import sys
import os
from agno.agent import Agent
from agno.models.groq import Groq  # Import Groq

# Add backend directory to path if not already there
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from api_manager import api_manager
except ImportError:
    # Fallback: try to import directly
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from api_manager import api_manager

def get_ner_agent():
    """
    Creates and returns a NerAgent with the current model from the ApiManager.
    """
    try:
        model = api_manager.get_model()
        if model is None:
            print("❌ ERROR: api_manager.get_model() returned None")
            return None
            
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
            agent_params['parser_model'] = Groq(id="openai/gpt-oss-120b", api_key=api_manager.groq_keys[0])

        agent = Agent(**agent_params)
        print("✅ NER Agent initialized successfully")
        return agent
    except Exception as e:
        print(f"❌ ERROR creating NER agent: {e}")
        import traceback
        traceback.print_exc()
        return None
