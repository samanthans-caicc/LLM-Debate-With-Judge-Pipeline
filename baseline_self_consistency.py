# baseline_self_consistency.py — Baseline 2: Self-Consistency with majority vote.
#
# Samples N independent CoT answers from a single model and takes the majority vote
# (Wang et al., 2023). N = 14 to match the total LLM calls in the debate pipeline
# (full 3-round run, no early exit).
#
# LLM call breakdown in the debate pipeline (N=14):
#   Proponent initial (1) + Opponent initial (1) + check_agreement post-init (1)
#   + [Proponent (1) + Opponent (1) + check_agreement (1)] x 3 rounds
#   + Judge (1) + evaluate_verdict (1) = 14
#
# Usage:
#   python baseline_self_consistency.py --dataset strategyqa --n 100 --seed 42
#   python baseline_self_consistency.py --dataset arc --n 100 --samples 14 --seed 42
#   python baseline_self_consistency.py --questions-file tests/batch_20260312_221358/batch_questions_20260313_022552.json

import argparse
import json
import os
from collections import Counter
from datetime import datetime

from config import client, model, DEBATE_HYPERPARAMETERS
from dataset_loader import load_strategyqa, load_arc
from main import _extract_yes_no


N_SAMPLES = 14  # Matches total LLM calls in a full debate pipeline run

SELF_CONSISTENCY_SYSTEM = (
    "You are a knowledgeable assistant. Answer questions accurately and concisely. "
    "Think step by step before giving your final answer."
)


def _single_cot_call(problem_context: str, candidate_answer: str) -> str:
    """One CoT call — returns raw response text."""
    prompt = (
        f"Problem: {problem_context}\n\n"
        f"Candidate Answer: {candidate_answer}\n\n"
        f"Think step by step. Then end your response with exactly one of these verdicts "
        f"on its own line: CORRECT or INCORRECT."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SELF_CONSISTENCY_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        stream=False,
    )
    return response.choices[0].message.content.strip()


def _extract_verdict(response: str) -> str:
    """Extract CORRECT or INCORRECT from a CoT response. Defaults to INCORRECT."""
    upper = response.upper()
    # Check last 200 chars first (verdict is at the end)
    tail = upper[-200:]
    if "CORRECT" in tail and "INCORRECT" not in tail:
        return "CORRECT"
    if "INCORRECT" in tail:
        return "INCORRECT"
    # Fallback: scan full response
    if "CORRECT" in upper and "INCORRECT" not in upper:
        return "CORRECT"
    return "INCORRECT"


def self_consistency(problem_context: str, candidate_answer: str, n_samples: int) -> dict:
    """
    Sample n_samples CoT responses and take majority vote.
    Returns the majority verdict and the full vote tally.
    """
    verdicts = []
    responses = []

    for i in range(n_samples):
        resp = _single_cot_call(problem_context, candidate_answer)
        verdict = _extract_verdict(resp)
        verdicts.append(verdict)
        responses.append(resp)
        print(f"  Sample {i+1}/{n_samples}: {verdict}")

    tally = Counter(verdicts)
    majority = tally.most_common(1)[0][0]
    return {
        "majority_verdict": majority,
        "tally": dict(tally),
        "responses": responses,
    }


def _matches_ground_truth(majority_verdict: str, candidate_answer: str, ground_truth: str) -> bool:
    """
    Compare majority vote against ground truth via a lightweight LLM call.
    Reuses the same pattern as evaluate_verdict in main.py.
    """
    prompt = (
        f"A majority vote of {N_SAMPLES} independent CoT responses determined that "
        f"the candidate answer is: {majority_verdict}\n\n"
        f"Candidate Answer: {candidate_answer}\n"
        f"Ground Truth: {ground_truth}\n\n"
        f"Does the majority verdict align with the ground truth? "
        f"Reply with only YES or NO."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    answer = response.choices[0].message.content.strip()
    return _extract_yes_no(answer)


def run_self_consistency_batch(questions: list[dict], n_samples: int, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = []
    correct = 0

    for i, q in enumerate(questions, start=1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(questions)}] ID: {q['source_id']}")
        print(f"Context: {q['problem_context'][:100]}...")

        sc = self_consistency(q["problem_context"], q["candidate_answer"], n_samples)
        print(f"Majority: {sc['majority_verdict']}  |  Tally: {sc['tally']}")

        matches = _matches_ground_truth(
            sc["majority_verdict"], q["candidate_answer"], q["ground_truth"]
        )
        if matches:
            correct += 1
        print(f"Correct: {matches}")

        results.append({
            "source_id": q["source_id"],
            "problem_context": q["problem_context"],
            "candidate_answer": q["candidate_answer"],
            "ground_truth": q["ground_truth"],
            "majority_verdict": sc["majority_verdict"],
            "tally": sc["tally"],
            "verdict_matches_ground_truth": matches,
        })

    accuracy = correct / len(questions) if questions else 0
    print(f"\n{'='*60}")
    print(f"  SELF-CONSISTENCY RESULTS  (N={n_samples} samples)")
    print(f"{'='*60}")
    print(f"  Questions: {len(questions)}")
    print(f"  Correct:   {correct}")
    print(f"  Accuracy:  {accuracy:.2%}")

    output = {
        "baseline": "self_consistency",
        "model": model,
        "n_samples": n_samples,
        "hyperparameters": DEBATE_HYPERPARAMETERS,
        "timestamp": datetime.now().isoformat(),
        "n": len(questions),
        "correct": correct,
        "accuracy": accuracy,
        "results": results,
    }

    path = os.path.join(out_dir, f"self_consistency_{timestamp}.json")
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[Results saved to {path}]")
    return accuracy


def load_questions_from_file(path: str) -> list[dict]:
    """Load questions directly from a batch_questions_*.json index file."""
    with open(path) as f:
        data = json.load(f)
    questions = data["questions"]
    print(f"[Loaded {len(questions)} questions from {path}]")
    return questions


def main():
    parser = argparse.ArgumentParser(
        description="Baseline 2: Self-Consistency with majority vote (Wang et al., 2023)."
    )
    parser.add_argument("--questions-file", type=str, default=None,
                        help="Path to a batch_questions_*.json file to reuse exact questions from a prior debate run.")
    parser.add_argument("--dataset", choices=["strategyqa", "arc"], default="strategyqa",
                        help="Dataset to sample from (ignored if --questions-file is set).")
    parser.add_argument("--n", type=int, default=100,
                        help="Number of questions to sample (ignored if --questions-file is set).")
    parser.add_argument("--samples", type=int, default=N_SAMPLES,
                        help=f"Number of CoT samples per question (default: {N_SAMPLES})")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (ignored if --questions-file is set).")
    parser.add_argument("--out", type=str, default="test_outputs/baselines")
    args = parser.parse_args()

    if args.questions_file:
        questions = load_questions_from_file(args.questions_file)
    else:
        n = max(100, min(200, args.n))
        if args.dataset == "strategyqa":
            questions = load_strategyqa(n, args.seed)
        else:
            questions = load_arc(n, args.seed)

    run_self_consistency_batch(questions, args.samples, args.out)


if __name__ == "__main__":
    main()
