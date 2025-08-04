from agno.agent import Agent
from agno.knowledge.json import JSONKnowledgeBase  # or other knowledge type
from agno.vectordb.mongodb import MongoDb
from dotenv import load_dotenv
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.embedder.google import GeminiEmbedder

load_dotenv()

# Connect to your existing MongoDB database
vector_db = MongoDb(
    collection_name="NewsverseCo",  # Your collection name
    db_url="mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/",
    embedder=GeminiEmbedder()
)

# Create knowledge base WITHOUT loading new documents
knowledge_base = JSONKnowledgeBase(
    path=[],  # Empty path since data already exists
    vector_db=vector_db
)

# DON'T call knowledge_base.load() - data already exists

# Create agent and query existing data
agent = Agent(model= Gemini(id="gemini-2.0-flash"), knowledge=knowledge_base, search_knowledge=True, debug_mode=True,tools=[DuckDuckGoTools()])
agent.print_response("Extract all the title from the database using knowledge_base", markdown=True)