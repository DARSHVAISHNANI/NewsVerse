from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.knowledge.json import JSONKnowledgeBase
from agno.vectordb.mongodb import MongoDb
from agno.models.google import Gemini
from dotenv import load_dotenv
from agno.embedder.google import GeminiEmbedder
from pathlib import Path

load_dotenv()
# MongoDB Atlas connection string
"""
Example connection strings:
"mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
"mongodb://localhost/?directConnection=true"
"""
mdb_connection_string = "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/"

COLLECTION_NAME = "NewsVerse"

vector_db = MongoDb(
        collection_name=COLLECTION_NAME,
        db_url=mdb_connection_string,
        wait_until_index_ready_in_seconds=300,
        wait_after_insert_in_seconds=60,
        embedder=GeminiEmbedder()
    )

knowledge_base = JSONKnowledgeBase(
    path=Path(r"C:\Users\darsh\Desktop\Main Documents Folder\NewsVerse\BBC_scraped_article_details.json"),
    vector_db= vector_db
)

knowledge_base.load(recreate=True)  # Comment out after first run

agent = Agent(
    knowledge=knowledge_base, 
    show_tool_calls=True, 
    model=Gemini(id="gemini-2.0-flash-lite", api_key="AIzaSyC3181Om2bXkBrHNVptE6UIGR_eO0r_4jE"),
    debug_mode=True)


agent.print_response("What information is avaliable in the knowledgebase data?", markdown=True)