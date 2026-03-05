# main.py — LLM Debate Pipeline (multi-round)
# Orchestrates N debate rounds: both debaters build on full history, then Judge decides.

from proponent import proponent_agent, proponent_initial_position
from opponent import opponent_agent, opponent_initial_position
from judge import judge_agent
# from config import NUM_ROUNDS


def present_question(problem_context, candidate_answer):
    return (
        f"Problem: {problem_context}\n\n"
        f"Candidate Answer under debate: {candidate_answer}"
    )


def _build_history(label, initial_position, responses):
    """Format a debater's full history (initial position + all round responses)."""
    history = f"--- {label}'s Initial Position ---\n{initial_position}\n"
    for i, resp in enumerate(responses, start=1):
        history += f"\n--- {label}'s Round {i} Response ---\n{resp}\n"
    return history


def run_debate(problem_context, candidate_answer):
    print("=" * 60)
    print("  *** LLM DEBATE PIPELINE: AGENTS AT WAR ***")
    print("=" * 60)
    print(f"\nProblem Context:\n{problem_context}")
    print(f"\nCandidate Answer:\n{candidate_answer}")

    # Phase 1: Present the same question to both debaters independently
    question = present_question(problem_context, candidate_answer)

    print("\n" + "=" * 60)
    print("  PHASE 1: INDEPENDENT INITIAL POSITIONS")
    print("=" * 60)
    print(f"\n[Question presented to both debaters independently]\n{question}")

    print("\n" + "-" * 60)
    print("PROPONENT'S INITIAL POSITION:")
    print("-" * 60)
    proponent_opening = proponent_initial_position(problem_context, candidate_answer)

    print("\n" + "-" * 60)
    print("OPPONENT'S INITIAL POSITION:")
    print("-" * 60)
    opponent_opening = opponent_initial_position(problem_context, candidate_answer)

    # Phase 2: Multi-round debate
    # Each agent sees the opponent's full history up to the previous round.
    proponent_responses = []
    opponent_responses = []

    # for round_num in range(1, NUM_ROUNDS + 1):
    #     print("\n" + "=" * 60)
    #     print(f"  PHASE 2, ROUND {round_num} of {NUM_ROUNDS}: DEBATE")
    #     print("=" * 60)

    #     # Each agent sees ALL of the opponent's prior output (initial + previous rounds)
    #     opponent_history = _build_history("Opponent", opponent_opening, opponent_responses)
    #     proponent_history = _build_history("Proponent", proponent_opening, proponent_responses)

    #     print("\n" + "-" * 60)
    #     print(f"PROPONENT ARGUES (Round {round_num}):")
    #     print("-" * 60)
    #     prop_resp = proponent_agent(
    #         problem_context=problem_context,
    #         candidate_answer=candidate_answer,
    #         opponent_history=opponent_history,
    #     )
    #     proponent_responses.append(prop_resp)

    #     print("\n" + "-" * 60)
    #     print(f"OPPONENT FIRES BACK (Round {round_num}):")
    #     print("-" * 60)
    #     opp_resp = opponent_agent(
    #         problem_context=problem_context,
    #         candidate_answer=candidate_answer,
    #         proponent_history=proponent_history,
    #     )
    #     opponent_responses.append(opp_resp)

    # Phase 3: Build full transcript and let the judge decide
    full_transcript = (
        "=== PROPONENT'S FULL DEBATE HISTORY ===\n"
        + _build_history("Proponent", proponent_opening, proponent_responses)
        + "\n=== OPPONENT'S FULL DEBATE HISTORY ===\n"
        + _build_history("Opponent", opponent_opening, opponent_responses)
    )

    print("\n" + "=" * 60)
    print("  JUDGMENT")
    print("=" * 60)
    print("\n" + "-" * 60)
    print("THE JUDGE DELIVERS THE VERDICT:")
    print("-" * 60)
    judge_agent(
        problem_context=problem_context,
        candidate_answer=candidate_answer,
        full_transcript=full_transcript,
    )
    print("=" * 60)


if __name__ == "__main__":
    problem_context = (
        "The internet is deeply divided on whether pineapple is an acceptable pizza topping. "
        "Proponents argue that the sweetness of pineapple creates a bold sweet-savory contrast "
        "that elevates the pizza experience. Critics insist that fruit has no place on pizza, "
        "citing texture degradation, moisture release, and the violation of Italian culinary tradition."
    )
    candidate_answer = "Pineapple belongs on pizza and anyone who disagrees has no taste."

    run_debate(problem_context, candidate_answer)
