from google.api_core.exceptions import ResourceExhausted
from Recommendation_Engine import db_manager
from Recommendation_Engine.agents import get_analysis_agent
from api_manager import api_manager
import logging

# --- Logging Setup ---
logger = logging.getLogger("UserAnalyzer")
logger.setLevel(logging.INFO)

def analyzeAllUsers(user_collection):
    """
    Analyzes preferences for all users, now with internal agent management.
    """
    users = db_manager.fetchAllUsersForAnalysis(user_collection)
    results = []

    for user in users:
        user_name = user.get("name", "Unknown User")
        ner_data = user.get("ner_data")

        if not ner_data:
            logger.warning(f"Skipping user '{user_name}' (no NER data).")
            continue

        logger.info(f"Analyzing preferences for user: '{user_name}'...")
        summary = None
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                analysis_agent = get_analysis_agent()
                response = analysis_agent.run(str(ner_data))
                
                # Extract the 'content' attribute from the RunOutput object
                if hasattr(response, 'content'):
                    summary = response.content
                else:
                    summary = str(response)
                    
                break 
            except ResourceExhausted:
                logger.warning("Gemini API rate limit exceeded. Switching to Groq...")
                api_manager.switch_to_groq()
            except Exception as e:
                logger.error(f"An unexpected error during user analysis: {e}", exc_info=True)
                break
        
        if summary:
            analysis_data = {
                "user_id": str(user["_id"]),
                "email": user["email"],
                "name": user_name,
                "detailed_summary": summary
            }
            results.append(analysis_data)
            logger.info(f"Generated preference summary for '{user_name}'.")
        else:
            logger.error(f"Failed to generate summary for '{user_name}'.")

    return results