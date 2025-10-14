import os
from collections import deque
from agno.models.google import Gemini
from agno.models.groq import Groq
# REMOVE the dotenv lines from this file

class ApiManager:
    """
    Manages API keys and models, with a fallback from Gemini to Groq.
    """
    def __init__(self, gemini_keys, groq_keys):
        if not gemini_keys or not all(k for k in gemini_keys):
            raise ValueError("Gemini API keys list cannot be empty or contain empty strings.")
        if not groq_keys or not all(k for k in groq_keys):
            raise ValueError("Groq API keys list cannot be empty or contain empty strings.")

        self.gemini_keys = deque(gemini_keys)
        self.groq_keys = deque(groq_keys)
        self.current_model_name = "gemini"

    def get_model(self):
        """
        Returns the current model instance based on the active service.
        """
        if self.current_model_name == "gemini":
            # Corrected to a valid model name like gemini-2.0-flash
            return Gemini(id="gemini-2.0-flash", api_key=self.gemini_keys[0])
        else: # Fallback to groq
             # Corrected to a valid llama3 model
            return Groq(id="openai/gpt-oss-120b", api_key=self.groq_keys[0])

    def switch_to_groq(self):
        """
        Switches the current model to Groq.
        """
        print("Switching to Groq model.")
        self.current_model_name = "groq"

    def get_current_model_name(self):
        return self.current_model_name

# Initialize the manager with keys from .env
gemini_api_keys = [key.strip() for key in os.getenv("GEMINI_API_KEYS", "").split(',') if key.strip()]
groq_api_keys = [key.strip() for key in os.getenv("GROQ_API_KEYS", "").split(',') if key.strip()]

# Create a single instance of the manager to be used across the application
api_manager = ApiManager(gemini_api_keys, groq_api_keys)