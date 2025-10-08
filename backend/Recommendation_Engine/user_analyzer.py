from google.api_core.exceptions import ResourceExhausted
from Recommendation_Engine import db_manager
from Recommendation_Engine.agents import get_analysis_agent # Import the agent creator
from api_manager import api_manager

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
            print(f"⏭️  Skipping user '{user_name}' (no NER data).")
            continue

        print(f"\nAnalyzing preferences for user: '{user_name}'...")
        summary = None
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                analysis_agent = get_analysis_agent() # Get fresh agent
                summary = analysis_agent.run(str(ner_data))
                break 
            except ResourceExhausted:
                print("🚨 Gemini API rate limit exceeded. Switching to Groq...")
                api_manager.switch_to_groq()
            except Exception as e:
                print(f"An unexpected error during user analysis: {e}")
                break
        
        if summary:
            analysis_data = {
                "user_id": str(user["_id"]),
                "email": user["email"],
                "name": user_name,
                "detailed_summary": summary
            }
            results.append(analysis_data)
            print(f"✅ Generated preference summary for '{user_name}'.")
        else:
            print(f"❌ Failed to generate summary for '{user_name}'.")

    return results