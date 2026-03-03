# API setup.
import os
from openai import OpenAI

# Set up API client
api_key = os.environ.get("UTSA_API_KEY")
base_url = os.environ.get("UTSA_BASE_URL")
model = os.environ.get("UTSA_MODEL")
# Note: API key, base URL, and model to be input into venv terminal manually
# via export commands, e.g. export UTSA_API_KEY='api_key_here'

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

# Hyperparameters for the debate
DEBATE_HYPERPARAMETERS = {
    "temperature": 0.7,  # Controls creativity of responses
    "max_tokens": 4098,   # Max tokens for each agent's response
    "top_p": 0.9,        # Nucleus sampling for response diversity
}