from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

async def main(): 
    model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    assitant = AssistantAgent(name="assistant", model_client=model_client)

    reuslt = await assitant.run(task="What is the capital of India?")

    print(reuslt)
    print("\n")
    print(reuslt.messages)
    print("\n")
    print(reuslt.messages[-1].content)
    print("\n")
    
    

asyncio.run(main())