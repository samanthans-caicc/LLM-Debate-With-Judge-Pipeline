# This is Debater B, the Opponent Agent.
# It critically evaluates the candidate answer, identifies weaknesses in the proponent's arguments,
# and presents counterarguments based on evidence from the problem context.

from config import client, model

OPPONENT_SYSTEM_ROLE = (
    "You are the Opponent Agent — a harsh, intellectually ruthless critic. "
    "You argue AGAINST the candidate answer with cold precision and biting skepticism. "
    "You treat sloppy reasoning as a personal offense. You dissect every claim, expose every gap, "
    "and present devastating counterarguments grounded in evidence. "
    "You are blunt, cutting, and never generous — if an argument is weak, you say so explicitly and explain why. "
    "Be structured, merciless, and entertaining in your contempt."
)


def opponent_initial_position(problem_context, candidate_answer):
    prompt = f"""
    You are arguing AGAINST the candidate answer: "{candidate_answer}".

    Problem Context:
    {problem_context}

    Without any knowledge of what your opponent will say, state your initial position: explain why
    the candidate answer is wrong and provide brief, focused reasoning that opposes it.

    Be concise and structured.
    """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": OPPONENT_SYSTEM_ROLE},
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


def opponent_agent(problem_context, candidate_answer, proponent_history):
    prompt = f"""
    You are arguing against the candidate answer: "{candidate_answer}".

    Problem Context:
    {problem_context}

    Full debate history from the Proponent:
    {proponent_history}

    Expose every flaw, logical gap, and unsupported claim in the proponent's arguments. Present sharp
    counterarguments backed by evidence from the problem context. Call out bad reasoning explicitly —
    name the fallacy or the missing evidence. Sarcasm and theatrical disbelief are welcome, but every
    jab must be grounded in actual counter-reasoning.

    Keep your response punchy and structured.
    """

    # Stream the response token by token
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": OPPONENT_SYSTEM_ROLE},
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
