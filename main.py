# main.py — LLM Debate Pipeline (single-round)
# Orchestrates one full debate round: Proponent argues → Opponent rebuts → Judge decides.

from proponent import proponent_agent
from opponent import opponent_agent
from judge import judge_agent
import config  # Ensure API client and hyperparameters are set up

def run_debate(problem_context, candidate_answer):
    print("=" * 60)
    print("  *** LLM DEBATE PIPELINE: AGENTS AT WAR ***")
    print("=" * 60)
    print(f"\nProblem Context:\n{problem_context}")
    print(f"\nCandidate Answer:\n{candidate_answer}")

    # Round 1: Proponent argues in favor (no counterarguments yet)
    print("\n" + "-" * 60)
    print("PROPONENT ARGUES (smugly):")
    print("-" * 60)
    proponent_arguments = proponent_agent(
        problem_context=problem_context,
        candidate_answer=candidate_answer,
        counterarguments="None yet.",
    )

    # Round 1: Opponent rebuts
    print("\n" + "-" * 60)
    print("OPPONENT FIRES BACK (ruthlessly):")
    print("-" * 60)
    opponent_arguments = opponent_agent(
        problem_context=problem_context,
        candidate_answer=candidate_answer,
        proponent_arguments=proponent_arguments,
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
