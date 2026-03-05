#This file contains the configuration settings for the debate application, including API setup and hyperparameters for the debate agents.

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
    "temperature": 0.8,  # Controls creativity of responses. Prior tests: 0.7
    "max_tokens": 2049,   # Max tokens for each agent's response. Prior tests: 4096
    "top_p": 0.9,        # Nucleus sampling for response diversity
}

# NUM_ROUNDS = 3  # Number of back-and-forth debate rounds (Phase 2)