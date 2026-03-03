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

    # Call the API to get the judge's response
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    problem_context = "The problem is about the impact of climate change on polar bear populations."
    candidate_answer = "Climate change is causing a decline in polar bear populations."
    proponent_arguments = "Studies show Arctic sea ice has decreased by 13% per decade, reducing hunting grounds for polar bears."
    opponent_arguments = "Some polar bear subpopulations have remained stable, suggesting local adaptation may offset broader climate effects."

    verdict = judge_agent(problem_context, candidate_answer, proponent_arguments, opponent_arguments)
    print(verdict)

# END of judge.py
