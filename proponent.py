# An LLM agent that argues in favor of a candidate answer. It must construct logically coherent arguments, cite evidence from the problem context, and rebut counterarguments from Debater B.
# This is Proponent Agent.

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

def proponent_initial_position(question):
    prompt = f"""
    You are the Proponent Agent — a sharp, confident debater who is absolutely certain you are right.

    You have been presented with the following question/problem:
    {question}

    Without any knowledge of what your opponent will say, state your initial position: give your
    answer clearly and provide brief, focused reasoning that supports it.

    Be concise and structured.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    full_response = ""
    for chunk in response:
        token = chunk.choices[0].delta.content or ""
        print(token, end="", flush=True)
        full_response += token
    print()
    return full_response


def proponent_agent(problem_context, candidate_answer, counterarguments):
    # Construct the prompt for the proponent agent
    prompt = f"""
    You are the Proponent Agent — a sharp, confident debater who is absolutely certain you are right.
    You are arguing in favor of the candidate answer: "{candidate_answer}".

    Problem Context:
    {problem_context}

    Counterarguments from your opponent (Debater B):
    {counterarguments}

    Your task is to construct logically coherent arguments supporting the candidate answer, cite evidence
    from the problem context, and thoroughly dismantle the opponent's counterarguments.

    You may also throw in witty insults and condescending remarks directed at your opponent's intelligence
    and the quality of their arguments. Be theatrical, a little smug, and entertaining — but always back
    it up with actual reasoning.

    Keep your response punchy and structured.
    """
    
    # Stream the response token by token
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    full_response = ""
    for chunk in response:
        token = chunk.choices[0].delta.content or ""
        print(token, end="", flush=True)
        full_response += token
    print()
    return full_response

# Example usage
if __name__ == "__main__":
    problem_context = "The internet is deeply divided on whether pineapple is an acceptable pizza topping."
    candidate_answer = "Pineapple belongs on pizza and anyone who disagrees has no taste."
    counterarguments = "Fruit has no place on pizza. It ruins the texture and disrespects Italian tradition."
    
    proponent_response = proponent_agent(problem_context, candidate_answer, counterarguments)
    print(proponent_response)

# END of proponent.py
