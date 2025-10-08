from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.mongodb import MongoDb
from agno.models.google import Gemini
from dotenv import load_dotenv
from agno.embedder.google import GeminiEmbedder

load_dotenv()
# MongoDB Atlas connection string
"""
Example connection strings:
"mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
"mongodb://localhost/?directConnection=true"
"""
mdb_connection_string = "mongodb+srv://darshvaishnani1234:wAssPV9RS3dm55la@newscluster.p2duvnj.mongodb.net/"

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    vector_db=MongoDb(
        collection_name="recipes",
        db_url=mdb_connection_string,
        wait_until_index_ready_in_seconds=300,
        wait_after_insert_in_seconds=60,
        embedder=GeminiEmbedder()
    )
)  # adjust wait_after_insert and wait_until_index_ready to your needs

knowledge_base.load(recreate=True)  # Comment out after first run

agent = Agent(knowledge=knowledge_base, show_tool_calls=True, model=Gemini(id="gemini-2.0-flash-lite", api_key="AIzaSyC3181Om2bXkBrHNVptE6UIGR_eO0r_4jE"),debug_mode=True)
agent.print_response("How thai is being created", markdown=True)