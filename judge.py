# judge.py — Judge Agent.
# Evaluates the complete debate transcript and delivers a structured four-section
# ruling in Phase 3. Prompt is defined in prompts.py.

from config import client, model
from prompts import JUDGE_SYSTEM_ROLE, judge_prompt


def judge_agent(problem_context: str, candidate_answer: str, full_transcript: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_ROLE},
            {"role": "user",   "content": judge_prompt(problem_context, candidate_answer, full_transcript)},
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
