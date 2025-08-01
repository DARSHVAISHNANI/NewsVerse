from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools
from agno.models.google import Gemini

agent = Agent(
    name="Hackernews Team",
    model= Gemini(id="gemini-2.0-flash", api_key="AIzaSyAjAPLXDeEBmku4stwSm4-lFn3cKDq-aUY"),
    tools=[HackerNewsTools(get_top_stories=2)],
    show_tool_calls=True,
    markdown=True,
)

agent.print_response(
    "Provide me one of the latest news with title",
)