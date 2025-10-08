import asyncio
import json
import os
from dotenv import load_dotenv
from browser_use import *
from browser_use.llm import ChatGoogle
from pydantic import BaseModel
from typing import List, Optional

load_dotenv()


async def main():
    """
    Initializes an agent to extract structured data from a Reuters article,
    runs the agent, prints the result, and saves it to a JSON file.
    """
    agent = Agent(
        task="""
        Step-1: Got to this URL: https://www.reuters.com/world/asia-pacific/thailand-rejects-international-mediation-end-fighting-with-cambodia-2025-07-25/
        
        Step-2: Wait until it open the website
        Step-3: Extract the title of the news article
        Step-4: Extract the full description/HTML of the news article
        Step-5: Extract the url, date and time of the news article
        Step-6: Extract the source of the news article
        Step-7: Store this output in a JSON file.""",
        llm=ChatGoogle(model="gemini-1.5-flash",
                       api_key=os.getenv("GOOGLE_API_KEY"))
    )

    history = await agent.run()
    print(history)

    # results = history.messages[-1].content
    # print(results)

if __name__ == "__main__":
    asyncio.run(main())
