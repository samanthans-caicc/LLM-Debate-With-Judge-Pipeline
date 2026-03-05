# This is Debater B, the Opponent Agent.
# It critically evaluates the candidate answer, identifies weaknesses in the proponent's arguments,
# and presents counterarguments based on evidence from the problem context.

from config import client, model

def opponent_initial_position(problem_context, candidate_answer):
    prompt = f"""
    You are the Opponent Agent (Debater B) — a ruthless critic who takes great pleasure in tearing apart
    weak arguments. You are arguing AGAINST the candidate answer: "{candidate_answer}".

    Problem Context:
    {problem_context}

    Without any knowledge of what your opponent will say, state your initial position: explain why
    the candidate answer is wrong and provide brief, focused reasoning that opposes it.

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


def opponent_agent(problem_context, candidate_answer, proponent_history):
    # Construct the prompt for the opponent agent
    prompt = f"""
    You are the Opponent Agent (Debater B) — a ruthless critic who takes great pleasure in tearing apart
    weak arguments. You are arguing against the candidate answer: "{candidate_answer}".

    Problem Context:
    {problem_context}

    Full debate history from the Proponent (brace yourself, it's rough):
    {proponent_history}

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
