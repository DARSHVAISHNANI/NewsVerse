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

class ArticleTitle(BaseModel):
    title: str

#1. Atlas Connection
MONGODB_ATLAS_URI = "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/"

client = MongoClient(MONGODB_ATLAS_URI, tlsCAFile=certifi.where())

db = client["NewsVerseDB"]  # Replace with your DB name
collection = db["NewsVerseCo"]  # Replace with your collection name


# 2. Extract all 'title' fields from the collection
titles = [doc.get("title") for doc in collection.find({}, {"title": 1, "_id": 0}) if doc.get("title")]

if not titles:
    raise ValueError("No titles found in the collection.")


# 3. Define a creative agent that generates a new article title
title_gen_agent = Agent(
    name="TitleGenAgent",
    model=Gemini(id="gemini-2.0-flash"),
    instructions=(
        "You will be given a list of article titles.\n"
        "Reply with a JSON object containing a single key 'title' with a new creative article title as the value.\n"
        "Example:\n"
        '{ "title": "Your suggested article title here" }\n\n'
        "Titles:\n" + "\n".join(titles)
    ),
    tools=[DuckDuckGoTools(), WebBrowserTools()],
    add_history_to_messages=False,
    markdown=True,
    debug_mode=True,
    show_tool_calls=True
)

# 4. Run the agent and generate the new title
result = title_gen_agent.run("Suggest a new article title inspired by the list above.")
content = result.content.strip()

try:
    data = json.loads(content)
    article_title = ArticleTitle(**data)
except json.JSONDecodeError:
    # fallback if output is plain text
    article_title = ArticleTitle(title=content)

print("New Article Title:", result.content)
print("Formatted Article: ", article_title.title)