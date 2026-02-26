# An LLM agent that argues in favor of a candidate answer. It must construct logically coherent arguments, cite evidence from the problem context, and rebut counterarguments from Debater B.

import os
from openai import OpenAI

# Set up API client
api_key = os.environ.get("UTSA_API_KEY")
base_url = os.environ.get("UTSA_BASE_URL")
model = os.environ.get("UTSA_MODEL")
# Note: API key, base URL, and model to be input into venv terminal manually via export commands, e.g. export UTSA_API_KEY='api_key_here'

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

def proponent_agent(problem_context, candidate_answer, counterarguments):
    # Construct the prompt for the proponent agent
    prompt = f"""
    You are Proponent Agent, arguing in favor of the candidate answer: "{candidate_answer}".
    
    Problem Context:
    {problem_context}
    
    Counterarguments from Debater B:
    {counterarguments}
    
    Your task is to construct logically coherent arguments supporting the candidate answer, citing evidence from the problem context, and rebutting the counterarguments.
    
    Please provide your arguments in a clear and structured manner.
    """
    
    # Call the API to get the proponent's response
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    
    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    problem_context = "The problem is about the impact of climate change on polar bear populations."
    candidate_answer = "Climate change is causing a decline in polar bear populations."
    counterarguments = "Some argue that polar bear populations are stable and not significantly affected by climate change."
    
    proponent_response = proponent_agent(problem_context, candidate_answer, counterarguments)
    print(proponent_response)

# END of proponent.py
