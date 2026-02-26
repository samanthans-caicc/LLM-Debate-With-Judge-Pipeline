# An LLM agent that argues in favor of a candidate answer. It must construct logically coherent arguments, cite evidence from the problem context, and rebut counterarguments from Debater B.

import os
from openai import OpenAI

api_key = os.environ.get("UTSA_API_KEY")
base_url = os.environ.get("UTSA_BASE_URL")
model = os.environ.get("UTSA_MODEL")

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)


