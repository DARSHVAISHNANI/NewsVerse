from agno.agent import Agent
from textwrap import dedent
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.tools.crawl4ai import Crawl4aiTools
from agno.tools.duckduckgo import DuckDuckGoTools
import os
from dotenv import load_dotenv
import time
load_dotenv()

start_time = time.time()
#Create a agent that can extract latest news topic on which article url can be crawl
Latest_Article_Searcher = Agent(
    name="TopicExtractor",
    model=Groq(id="qwen/qwen3-32b"),
    description=(
        "You're an expert web researcher who specializes in identifying the most trending and relevant news topics "
        "that people are currently reading. Your job is to search the internet using DuckDuckGo, extract the titles "
        "or themes of the most talked-about or recent articles, and prepare them for further processing."
    ),
    instructions=[
        "Use DuckDuckGo to search for the latest trending news articles.",
        "From the top 5 search results, extract clear and concise topic names that best describe the article content.",
        "Return only the topic name (not the URL or summary) to the URLFetcher tool.",
        "Avoid repeating the same topic in different forms.",
        "Ensure the topic is fresh, relevant, and easy to understand."
    ],
    tools=[DuckDuckGoTools()],
    markdown=True,
    show_tool_calls=True
)

#Create a agent that can extract latest news article url
URL_Extractor_Agent = Agent(
    name="URLFetcher",
    model =Groq(id="qwen/qwen3-32b"),
    description="You are an expert content finder. Your task is to find the URL of the latest article on any topic but must be latest.",
    instructions= [
         "Use Crawl4ai tool to search for articles.",
        "Return the URL of the article with the latest publication date.",
        "If no publication date is found, use the first valid article."
    ],
    tools=[Crawl4aiTools()],
    markdown=True,
    show_tool_calls=True
)

# Using Crawl4ai, extract the contain of each url that is extracted by ArticleFetcher will given.
# crawl_toolkit = Crawl4aiToolkit()
Article_Extract_agent = Agent(
    name="ArticleFetcher",
    model=Groq(id="qwen/qwen3-32b"),
    description= "You are an expert news content extractor.",
    instructions= dedent("""
    You are an expert news content extractor.

    From the provided URL, extract **only the latest news article** in the following structured format:

    - title: The exact headline of the article
    - full_description: The complete body or main content of the article must be atlest 200 words.
    - source: The website or publication source (e.g., Bloomberg, BBC, The New york times)
    - date: The publishing date in YYYY-MM-DD format if available. 
      If not present in metadata, scan the page for phrases like "Published on July 18, 2025".
    - time: The publishing time in HH:MM format if available. 
      Look for metadata or extract from text like "8:34 AM" or "08:34".
    - url: The URL of the news article and make sure that the url is working properly or other wise the URL_Extractor url must be paste which is accessable to user.

    If multiple articles are on the page, choose the most recent or most prominent one. 
    Be precise and use pattern matching where metadata is missing.
    """).strip(),
    tools=[Crawl4aiTools(max_length=1000)],
    reasoning=True,
    markdown=True,
    show_tool_calls=True
)

#Combine this both ai agent to create a team
agent_team = Agent(
    team=[Latest_Article_Searcher, URL_Extractor_Agent, Article_Extract_agent],
    model=Groq(id="qwen/qwen3-32b"),
    instructions=["First execute the url from the URL_Extractor_Agent and then take each url and Extract or web scrape the article content of each url in a structured format like title, full_description, source, date, time, and paste the url from the agent."],
    markdown=True,
    show_tool_calls=True,
    monitoring=True
)

agent_team.print_response(
    "Step 1: Use TopicExtractor to identify trending news topics that people are reading today.\n"
    "Step 2: For each topic, use URLFetcher to find the most recent article URL from a well-known news site as much as possible.\n"
    "Step 3: For each URL, use Crawl4ai with WebCrawler to extract structured article content including:\n"
    "- title\n- full_description atlest 200 words long\n- source\n- date\n- time\n- url\n\n"
    "Return the final output as a list of structured news articles.",
    stream=True
)

end_time = time.time()

print("Total Time Taken To Run: "+ str(end_time-start_time))