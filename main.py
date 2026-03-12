# main.py — LLM Debate Pipeline (multi-round)
# Orchestrates N debate rounds: both debaters build on full history, then Judge decides.

import json
import os
from datetime import datetime

from config import client, model, NUM_ROUNDS
from proponent import proponent_agent, proponent_initial_position
from opponent import opponent_agent, opponent_initial_position
from judge import judge_agent


def present_question(problem_context, candidate_answer):
    return (
        f"Problem: {problem_context}\n\n"
        f"Candidate Answer under debate: {candidate_answer}"
    )


def _build_full_transcript(proponent_opening, opponent_opening, proponent_responses, opponent_responses):
    """Build a chronological interleaved transcript of all complete rounds."""
    transcript = "=== INITIAL POSITIONS ===\n"
    transcript += f"[Proponent]\n{proponent_opening}\n\n"
    transcript += f"[Opponent]\n{opponent_opening}\n"
    for i, (p, o) in enumerate(zip(proponent_responses, opponent_responses), start=1):
        transcript += f"\n=== ROUND {i} ===\n"
        transcript += f"[Proponent]\n{p}\n\n"
        transcript += f"[Opponent]\n{o}\n"
    return transcript


def check_agreement(prop_response, opp_response):
    """Returns True if both debaters appear to agree on the same conclusion."""
    prompt = (
        "Below are responses from two debaters. Determine whether both debaters are now "
        "expressing agreement or convergence on the same conclusion — meaning neither is "
        "meaningfully opposing the other anymore.\n\n"
        f"Proponent's response:\n{prop_response}\n\n"
        f"Opponent's response:\n{opp_response}\n\n"
        "Reply with only YES or NO."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    answer = response.choices[0].message.content.strip().upper()
    return answer.startswith("YES")


def evaluate_verdict(judge_response, candidate_answer, ground_truth):
    """Compare the judge's verdict against the ground truth. Returns a result dict."""
    if ground_truth is None:
        return {"verdict_matches_ground_truth": None, "explanation": "No ground truth provided."}

    prompt = (
        f"A debate was held about the following candidate answer:\n"
        f"  Candidate Answer: {candidate_answer}\n\n"
        f"The ground truth is:\n"
        f"  {ground_truth}\n\n"
        f"The judge's full ruling is:\n"
        f"{judge_response}\n\n"
        f"Does the judge's final verdict select the answer that best aligns with the ground truth?\n"
        f"Start your response with YES or NO, then explain in 2-3 sentences."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    explanation = response.choices[0].message.content.strip()
    matches = explanation.upper().startswith("YES")
    return {"verdict_matches_ground_truth": matches, "explanation": explanation}


def save_transcript(transcript: dict):
    os.makedirs("test_outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"test_outputs/transcript_{timestamp}.json"
    with open(path, "w") as f:
        json.dump(transcript, f, indent=2)
    print(f"\n[Transcript saved to {path}]")


def run_debate(problem_context, candidate_answer, ground_truth=None):
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

    # Phase 1, Requirement 3: Check for consensus on initial positions
    proponent_responses = []
    opponent_responses = []
    early_exit_round = None

    if check_agreement(proponent_opening, opponent_opening):
        print("\n[Both debaters agree on initial positions. Skipping to judgment.]")
    else:
        # Phase 2: Multi-round debate (N >= 3 rounds)
        consecutive_agreements = 0
        for round_num in range(1, NUM_ROUNDS + 1):
            print("\n" + "=" * 60)
            print(f"  PHASE 2, ROUND {round_num} of {NUM_ROUNDS}: DEBATE")
            print("=" * 60)

            # Req 2: Both agents receive the full interleaved transcript of all previous rounds
            prev_transcript = _build_full_transcript(
                proponent_opening, opponent_opening, proponent_responses, opponent_responses
            )

            print("\n" + "-" * 60)
            print(f"PROPONENT ARGUES (Round {round_num}):")
            print("-" * 60)
            prop_resp = proponent_agent(
                problem_context=problem_context,
                candidate_answer=candidate_answer,
                full_transcript=prev_transcript,
            )
            proponent_responses.append(prop_resp)

            # Opponent also sees the proponent's argument from this round
            opponent_context = prev_transcript + f"\n=== ROUND {round_num} ===\n[Proponent]\n{prop_resp}\n"

            print("\n" + "-" * 60)
            print(f"OPPONENT FIRES BACK (Round {round_num}):")
            print("-" * 60)
            opp_resp = opponent_agent(
                problem_context=problem_context,
                candidate_answer=candidate_answer,
                full_transcript=opponent_context,
            )
            opponent_responses.append(opp_resp)

            # Req 3: Adaptive stopping — exit only after TWO consecutive rounds of agreement
            if check_agreement(prop_resp, opp_resp):
                consecutive_agreements += 1
                print(f"\n[Agreement detected — {consecutive_agreements} consecutive round(s).]")
                if consecutive_agreements >= 2:
                    early_exit_round = round_num
                    print("[Two consecutive rounds of agreement. Skipping to judgment.]")
                    break
            else:
                consecutive_agreements = 0

    # Phase 3: Build full transcript and let the judge decide
    full_transcript = _build_full_transcript(
        proponent_opening, opponent_opening, proponent_responses, opponent_responses
    )

    print("\n" + "=" * 60)
    print("  JUDGMENT")
    print("=" * 60)
    print("\n" + "-" * 60)
    print("THE JUDGE DELIVERS THE VERDICT:")
    print("-" * 60)
    judge_response = judge_agent(
        problem_context=problem_context,
        candidate_answer=candidate_answer,
        full_transcript=full_transcript,
    )
    print("=" * 60)

    # Phase 4: Evaluate judge's verdict against ground truth
    print("\n" + "=" * 60)
    print("  PHASE 4: EVALUATION")
    print("=" * 60)
    evaluation = evaluate_verdict(judge_response, candidate_answer, ground_truth)
    print(f"\nGround Truth:\n{ground_truth}")
    print(f"\nVerdict matches ground truth: {evaluation['verdict_matches_ground_truth']}")
    print(f"\nExplanation:\n{evaluation['explanation']}")
    print("=" * 60)

    transcript = {
        "timestamp": datetime.now().isoformat(),
        "problem_context": problem_context,
        "candidate_answer": candidate_answer,
        "ground_truth": ground_truth,
        "question": question,
        "initial_positions": {
            "proponent": proponent_opening,
            "opponent": opponent_opening,
        },
        "rounds": [
            {"round": i + 1, "proponent": p, "opponent": o}
            for i, (p, o) in enumerate(zip(proponent_responses, opponent_responses))
        ],
        "early_exit_round": early_exit_round,
        "judge_response": judge_response,
        "evaluation": evaluation,
    }
    save_transcript(transcript)


if __name__ == "__main__":
    problem_context = (
        "The internet is deeply divided on whether pineapple is an acceptable pizza topping. "
        "Proponents argue that the sweetness of pineapple creates a bold sweet-savory contrast "
        "that elevates the pizza experience. Critics insist that fruit has no place on pizza, "
        "citing texture degradation, moisture release, and the violation of Italian culinary tradition."
    )
    candidate_answer = "Pineapple belongs on pizza and anyone who disagrees has no taste."

    ground_truth = "Pineapple on pizza is a matter of personal taste with no objectively correct answer."

    run_debate(problem_context, candidate_answer, ground_truth=ground_truth)
