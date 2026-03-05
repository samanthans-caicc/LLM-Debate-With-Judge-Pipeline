# This is the Judge Agent.
# It evaluates the arguments presented by both the Proponent and Opponent agents, assesses the strength
# of their reasoning, and determines which side has a more compelling case based on evidence and logic.

from config import client, model

def judge_agent(problem_context, candidate_answer, full_transcript):
    # Construct the prompt for the judge agent
    prompt = f"""
    You are the Judge — a no-nonsense, dramatic arbitrator who has seen too many terrible debates and is
    not afraid to say so. You are evaluating a multi-round debate about: "{candidate_answer}".

    Problem Context:
    {problem_context}

    Full Debate Transcript (all rounds):
    {full_transcript}

    Your task is to:
    1. Roast both debaters for their weakest moments before getting to the actual evaluation.
    2. Assess the logical coherence and evidence quality of both sides across all rounds.
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
