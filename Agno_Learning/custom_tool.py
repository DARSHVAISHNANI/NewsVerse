# predict_tool.py
from agno.agent import Agent
from agno.tools import tool
from agno.models.groq import Groq
from transformers import pipeline

# 1. Define the custom tool
# Load summarization model once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@tool(
    name="hf_summarizer",
    description="Summarize long text using Hugging Face BART model",
    show_result=True
)
def summarize_text(text: str, max_length: int = 150, min_length: int = 30) -> str:
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]["summary_text"]

agent = Agent(
    tools=[summarize_text],
    model=Groq(id="openai/gpt-oss-120b", api_key="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"),
    debug_mode=True,
    show_tool_calls=True,
    markdown=True
)

# Example usage
agent.print_response(
    "Summarize this text: 'Artificial Intelligence is transforming industries by automating tasks, improving efficiency, and unlocking new insights from data. It powers applications from chatbots to autonomous vehicles, shaping the future of work and society.'"
)