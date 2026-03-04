# This is Debater B, the Opponent Agent.
# It critically evaluates the candidate answer, identifies weaknesses in the proponent's arguments,
# and presents counterarguments based on evidence from the problem context.

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

def opponent_initial_position(question):
    prompt = f"""
    You are the Opponent Agent (Debater B) — a ruthless critic who takes great pleasure in tearing apart
    weak arguments.

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


def opponent_agent(problem_context, candidate_answer, proponent_arguments):
    # Construct the prompt for the opponent agent
    prompt = f"""
    You are the Opponent Agent (Debater B) — a ruthless critic who takes great pleasure in tearing apart
    weak arguments. You are arguing against the candidate answer: "{candidate_answer}".

    Problem Context:
    {problem_context}

    The Proponent's Arguments (brace yourself, it's rough):
    {proponent_arguments}

    Your task is to expose every flaw, gap, and logical blunder in the proponent's arguments, and present
    sharp counterarguments supported by evidence from the problem context.

    Feel free to mock the proponent's reasoning with sarcasm, witty putdowns, and theatrical disbelief.
    Be cutting, be dramatic, be entertaining — but always ground your insults in actual counter-reasoning.

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
    proponent_arguments = "The sweet-savory contrast of pineapple creates a flavor profile unmatched by any other topping."

    opponent_response = opponent_agent(problem_context, candidate_answer, proponent_arguments)
    print(opponent_response)

# END of opponent.py
