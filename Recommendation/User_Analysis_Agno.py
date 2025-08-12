import json
import certifi
from agno.agent import Agent
from dotenv import load_dotenv
from pymongo import MongoClient
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.webbrowser import WebBrowserTools

load_dotenv()

# MongoDB Atlas connection
MONGODB_ATLAS_URI = "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/"
client = MongoClient(MONGODB_ATLAS_URI, tlsCAFile=certifi.where())
db = client["UserDB"]
collection = db["UserCo"]

# Fetch all users
users = collection.find({}, {"user_id": 1, "title_list": 1, "_id": 0})

for user in users:
    user_id = user.get("user_id")
    titles = [t.strip() for t in user.get("title_list", []) if t.strip()]
    
    if not titles:
        print(f"⚠️ No titles found for user {user_id}")
        continue

    # Create category analysis prompt
    instructions = (
        "You are an AI system that analyzes a user's news reading preferences.\n"
        "You will be given a list of article titles that the user has liked.\n"
        "Your task is to analyze the user's preferences based on the following categories:\n"
        "1. Politics & International Affairs\n"
        "2. Sports\n"
        "3. Technology & Innovation\n"
        "4. Business & Finance\n"
        "5. Entertainment & Lifestyle\n"
        "For each category, rate the user's interest from 0 to 10, where 0 means no interest and 10 means high interest.\n"
        "Also, provide a short analysis paragraph explaining the reasoning.\n"
        "Output the result as JSON in the following format:\n"
        "{\n"
        "  \"category_scores\": {\n"
        "    \"Politics & International Affairs\": 0-10,\n"
        "    \"Sports\": 0-10,\n"
        "    \"Technology & Innovation\": 0-10,\n"
        "    \"Business & Finance\": 0-10,\n"
        "    \"Entertainment & Lifestyle\": 0-10\n"
        "  },\n"
        "  \"analysis\": \"Your analysis here.\"\n"
        "}\n\n"
        "Titles:\n" + "\n".join(titles)
    )

    # Create agent
    pref_analysis_agent = Agent(
        name="UserPreferenceAnalyzer",
        model=Gemini(id="gemini-2.0-flash"),
        instructions=instructions,
        tools=[DuckDuckGoTools(), WebBrowserTools()],
        add_history_to_messages=False,
        markdown=True,
        debug_mode=True,
        show_tool_calls=True
    )

    # Run the AI analysis
    result = pref_analysis_agent.run("Analyze user preferences from the above titles.")
    content = result.content.strip()

    # Parse AI output
    try:
        analysis_data = json.loads(content)
    except json.JSONDecodeError:
        print(f"⚠️ Invalid JSON for {user_id}, storing raw output.")
        analysis_data = {"raw_output": content}

    # Save back to MongoDB
    collection.update_one(
        {"user_id": user_id},
        {"$set": {"preference_analysis": analysis_data}}
    )

    print(f"✅ Stored analysis for {user_id}")