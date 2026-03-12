# This is the Judge Agent.
# It evaluates the arguments presented by both the Proponent and Opponent agents, assesses the strength
# of their reasoning, and determines which side has a more compelling case based on evidence and logic.

from config import client, model

JUDGE_SYSTEM_ROLE = (
    "You are the Judge — a seasoned, no-nonsense arbitrator who has witnessed too many terrible debates "
    "and has zero patience for weak reasoning. You are fair but ruthless. "
    "You evaluate arguments on their logical coherence, use of evidence, and ability to rebut the opposition. "
    "You have a flair for the dramatic and are not afraid to roast both sides before delivering your verdict. "
    "Your rulings are final, well-reasoned, and entertainingly delivered. "
    "You always structure your ruling in exactly the four labeled sections specified."
)


def judge_agent(problem_context, candidate_answer, full_transcript):
    prompt = f"""
    You are evaluating a debate about the candidate answer: "{candidate_answer}".

    Original Question:
    Problem: {problem_context}
    Candidate Answer under debate: {candidate_answer}

    Full Debate Transcript (all rounds):
    {full_transcript}

    Deliver your ruling in exactly these four labeled sections:

    ## SECTION 1 — CHAIN-OF-THOUGHT ANALYSIS
    Walk through both debaters' arguments round by round. Trace how each side's reasoning evolved,
    where they strengthened or weakened their case, and how well they responded to each other.
    Be thorough. Roast the low points.

    ## SECTION 2 — ARGUMENT BREAKDOWN
    For each debater, explicitly identify:
    - Their STRONGEST argument (the one most logically sound and well-evidenced)
    - Their WEAKEST argument (the one most flawed, unsupported, or easily dismantled)

    ## SECTION 3 — FINAL VERDICT
    Declare a winner: "Proponent wins", "Opponent wins", or "It's a tie".
    State which answer you are selecting as the winning position and briefly justify it.
    Be decisive and dramatic.

    ## SECTION 4 — CONFIDENCE SCORE
    Rate your confidence in this verdict on a scale of 1 to 5:
      1 = Nearly a coin flip
      2 = Slight lean
      3 = Moderate confidence
      4 = Strong confidence
      5 = One side was completely dominant
    State the score and one sentence explaining it.
    """

    # Stream the response token by token
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_ROLE},
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
