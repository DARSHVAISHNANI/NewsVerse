import json
import certifi
from agno.agent import Agent
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.webbrowser import WebBrowserTools

load_dotenv()

class ArticleInfo(BaseModel):
    title: str
    url: str

# Atlas Connection
MONGODB_ATLAS_URI = "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/"
client = MongoClient(MONGODB_ATLAS_URI, tlsCAFile=certifi.where())
db = client["NewsVerseDB"]
collection = db["NewsVerseCo"]

# Extract all 'title' fields from the collection
titles = [doc.get("title") for doc in collection.find({}, {"title": 1, "_id": 0}) if doc.get("title")]
if not titles:
    raise ValueError("No titles found in the collection.")

# Step 1: Generate a new, creative article title (not present in DB)
title_gen_agent = Agent(
    name="TitleGenAgent",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=(
        "You will be given a list of article titles.\n"
        "Reply with a JSON object containing a single key 'title' with a new creative article title as the value.\n"
        "The title you suggest must NOT exactly match any titles in the list below.\n"
        "Example:\n"
        '{ \"title\": \"Your suggested article title here\" }\n\n'
        "Titles:\n" + "\n".join(titles)
    ),
    tools=[DuckDuckGoTools(), WebBrowserTools()],
    add_history_to_messages=False,
    markdown=True,
    debug_mode=True,
    show_tool_calls=True
)

result = title_gen_agent.run("Suggest a new article title inspired by the list above.")
content = result.content.strip()

# Robust JSON parsing
try:
    data = json.loads(content)
    new_title = data.get("title", "").strip()
except Exception:
    new_title = content.strip()

if not new_title or any(t.strip().lower() == new_title.lower() for t in titles):
    raise ValueError("Agent did not generate a unique article title!")

# Step 2: Use DuckDuckGoTools to search for a corresponding URL
search_agent = Agent(
    name="ArticleUrlAgent",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=(
        f"Find atmost 1 real web article URL that best matches this article title:\n'{new_title}'.\n"
        "Return the answer in a JSON object like {\"title\": ..., \"url\": ...}.\n"
        "Use the DuckDuckGo web search tool if needed."
    ),
    tools=[DuckDuckGoTools(), WebBrowserTools()],
    add_history_to_messages=False,
    markdown=True,
    debug_mode=True,
    show_tool_calls=True
)

search_result = search_agent.run(f"Find a real web URL for this title: {new_title}")
search_content = search_result.content.strip()

# Final parsing and Pydantic formatting
try:
    data = json.loads(search_content)
    article = ArticleInfo(**data)
except Exception:
    # Fallback: if not valid JSON, just make a record with the generated title and whatever is in the result
    article = ArticleInfo(title=new_title, url=search_content)

print("Suggested Article Title: ", article.title)
print("Referenced Article URL:  ", article.url)