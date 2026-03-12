# proponent.py — Proponent Agent (Debater A).
# Argues IN FAVOR of the candidate answer across Phase 1 (initial position)
# and Phase 2 (multi-round debate). Prompts are defined in prompts.py.

from config import client, model
from prompts import PROPONENT_SYSTEM_ROLE, proponent_initial_prompt, proponent_round_prompt


def _stream(messages) -> str:
    """Stream a chat completion and return the full response string."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    full_response = ""
    for chunk in response:
        token = chunk.choices[0].delta.content or ""
        print(token, end="", flush=True)
        full_response += token
    print()
    return full_response


def proponent_initial_position(problem_context: str, candidate_answer: str) -> str:
    return _stream([
        {"role": "system", "content": PROPONENT_SYSTEM_ROLE},
        {"role": "user",   "content": proponent_initial_prompt(problem_context, candidate_answer)},
    ])


def proponent_agent(problem_context: str, candidate_answer: str, full_transcript: str) -> str:
    return _stream([
        {"role": "system", "content": PROPONENT_SYSTEM_ROLE},
        {"role": "user",   "content": proponent_round_prompt(problem_context, candidate_answer, full_transcript)},
    ])
