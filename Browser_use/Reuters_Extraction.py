import asyncio
from dotenv import load_dotenv
load_dotenv()
from browser_use import Agent
from browser_use.llm import ChatGroq, ChatOpenRouter

async def main():
    agent = Agent(
        task="""Your task is to extract the latest news article url from this website: "https://www.reuters.com/" """,
        llm=ChatOpenRouter(model="moonshotai/kimi-k2:free", 
                           api_key="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", base_url="https://openrouter.ai/api/v1"),
    )
    await agent.run()

asyncio.run(main())