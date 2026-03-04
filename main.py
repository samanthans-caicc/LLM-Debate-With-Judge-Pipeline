# main.py — LLM Debate Pipeline (single-round)
# Orchestrates one full debate round: Proponent argues → Opponent rebuts → Judge decides.

from proponent import proponent_agent, proponent_initial_position
from opponent import opponent_agent, opponent_initial_position
from judge import judge_agent
import config  # Ensure API client and hyperparameters are set up

def present_question(problem_context, candidate_answer):
    return (
        f"Problem: {problem_context}\n\n"
        f"Candidate Answer under debate: {candidate_answer}"
    )


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
    proponent_opening = proponent_initial_position(question)

    print("\n" + "-" * 60)
    print("OPPONENT'S INITIAL POSITION:")
    print("-" * 60)
    opponent_opening = opponent_initial_position(question)

    # Phase 2: Debate — each agent now sees the other's initial position
    print("\n" + "=" * 60)
    print("  PHASE 2: DEBATE ROUND")
    print("=" * 60)

    print("\n" + "-" * 60)
    print("PROPONENT ARGUES (smugly):")
    print("-" * 60)
    proponent_arguments = proponent_agent(
        problem_context=problem_context,
        candidate_answer=candidate_answer,
        counterarguments=opponent_opening,
    )

    print("\n" + "-" * 60)
    print("OPPONENT FIRES BACK (ruthlessly):")
    print("-" * 60)
    opponent_arguments = opponent_agent(
        problem_context=problem_context,
        candidate_answer=candidate_answer,
        proponent_arguments=proponent_opening,
    )

    # Judge evaluates both sides and delivers a verdict
    print("\n" + "-" * 60)
    print("THE JUDGE DELIVERS THE VERDICT:")
    print("-" * 60)
    verdict = judge_agent(
        problem_context=problem_context,
        candidate_answer=candidate_answer,
        proponent_arguments=proponent_arguments,
        opponent_arguments=opponent_arguments,
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
