import autogen 

config_list = [
    {
        'model': 'meta-llama/llama-4-scout-17b-16e-instruct',
        'api_key': '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',
        'base_url': 'https://api.groq.com/openai/v1'
    }
]

llm_config={
    "seed": 42,
    "config_list": config_list
}

assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config=llm_config
)

user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    llm_config=llm_config,
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg = lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web", "use_docker": False},
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction. Otherwise, reply CONTINUE, or the reason why the task is not solved yet."""
)

task="""
Write a code to do web scraping of this url: "https://www.bbc.com/"
"""

user_proxy.initiate_chat(
    assistant,
    message=task
)