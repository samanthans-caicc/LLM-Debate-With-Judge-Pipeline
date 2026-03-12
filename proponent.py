# An LLM agent that argues in favor of a candidate answer. It must construct logically coherent arguments, cite evidence from the problem context, and rebut counterarguments from Debater B.
# This is Proponent Agent.

from config import client, model

PROPONENT_SYSTEM_ROLE = (
    "You are the Proponent Agent — a passionate, unshakeable true believer. "
    "You argue IN FAVOR of the candidate answer with total conviction. "
    "You are sharp, confident, and slightly smug. You never concede a point, "
    "and you always find a way to spin evidence in your favor. "
    "Be structured, persuasive, and entertainingly self-assured."
)


def proponent_initial_position(problem_context, candidate_answer):
    prompt = f"""
    You are arguing IN FAVOR of the candidate answer: "{candidate_answer}".

    Problem Context:
    {problem_context}

    Without any knowledge of what your opponent will say, state your initial position: explain why
    the candidate answer is correct and provide brief, focused reasoning that supports it.

    Be concise and structured.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PROPONENT_SYSTEM_ROLE},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )

    full_response = ""
    for chunk in response:
        token = chunk.choices[0].delta.content or ""
        print(token, end="", flush=True)
        full_response += token
    print()
    return full_response


def proponent_agent(problem_context, candidate_answer, opponent_history):
    prompt = f"""
    You are arguing in favor of the candidate answer: "{candidate_answer}".

    Problem Context:
    {problem_context}

    Full debate history from your opponent so far:
    {opponent_history}

    Construct logically coherent arguments supporting the candidate answer, cite evidence from the
    problem context, and thoroughly dismantle the opponent's counterarguments. You may throw in witty,
    condescending remarks about the quality of their reasoning — but always back it up with substance.

    Keep your response punchy and structured.
    """

    # Stream the response token by token
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": PROPONENT_SYSTEM_ROLE},
            {"role": "user", "content": prompt},
        ],
        stream=True,
    )

    full_response = ""
    for chunk in response:
        token = chunk.choices[0].delta.content or ""
        print(token, end="", flush=True)
        full_response += token
    print()
    return full_response
