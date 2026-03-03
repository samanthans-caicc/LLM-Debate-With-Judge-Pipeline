# This is the Judge Agent.
# It evaluates the arguments presented by both the Proponent and Opponent agents, assesses the strength
# of their reasoning, and determines which side has a more compelling case based on evidence and logic.

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

def judge_agent(problem_context, candidate_answer, proponent_arguments, opponent_arguments):
    # Construct the prompt for the judge agent
    prompt = f"""
    You are the Judge — a no-nonsense, dramatic arbitrator who has seen too many terrible debates and is
    not afraid to say so. You are evaluating a debate about: "{candidate_answer}".

    Problem Context:
    {problem_context}

    Proponent's Arguments:
    {proponent_arguments}

    Opponent's Arguments:
    {opponent_arguments}

    Your task is to:
    1. Roast both debaters for their weakest moments before getting to the actual evaluation.
    2. Assess the logical coherence and evidence quality of both sides.
    3. Declare a winner — "Proponent wins", "Opponent wins", or "It's a tie" — and be dramatic about it.

    Be entertaining, opinionated, and a little savage, but ultimately fair and well-reasoned.
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
    opponent_arguments = "Pineapple releases moisture that makes the crust soggy and ruins the entire structural integrity of the pizza."

    verdict = judge_agent(problem_context, candidate_answer, proponent_arguments, opponent_arguments)
    print(verdict)

# END of judge.py
