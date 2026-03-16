# baseline_direct_qa.py — Baseline 1: Direct QA with Chain-of-Thought prompting.
#
# A single LLM call answers each question directly using CoT — no debate.
#
# Usage:
#   python baseline_direct_qa.py --dataset strategyqa --n 100 --seed 42
#   python baseline_direct_qa.py --dataset arc --n 100 --seed 42
#   python baseline_direct_qa.py --questions-file tests/batch_20260312_221358/batch_questions_20260313_022552.json

import argparse
import json
import os
from datetime import datetime

from config import client, model, DEBATE_HYPERPARAMETERS
from dataset_loader import load_strategyqa, load_arc
from main import _extract_yes_no


DIRECT_QA_SYSTEM = (
    "You are a knowledgeable assistant. Answer questions accurately and concisely. "
    "Think step by step before giving your final answer."
)


def direct_qa(problem_context: str, candidate_answer: str) -> str:
    """Single CoT call — no debate, no agents."""
    prompt = (
        f"Problem: {problem_context}\n\n"
        f"Candidate Answer: {candidate_answer}\n\n"
        f"Think step by step, then state whether the candidate answer is correct or incorrect "
        f"and explain why in 2-3 sentences."
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": DIRECT_QA_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        stream=False,
    )
    return response.choices[0].message.content.strip()


def evaluate_direct_qa(response: str, candidate_answer: str, ground_truth: str) -> dict:
    """Check whether the direct QA response aligns with the ground truth."""
    prompt = (
        f"A model was asked whether the following candidate answer is correct:\n"
        f"  Candidate Answer: {candidate_answer}\n\n"
        f"The model responded:\n{response}\n\n"
        f"The ground truth is:\n  {ground_truth}\n\n"
        f"Does the model's response reach a conclusion that aligns with the ground truth? "
        f"Start your response with YES or NO, then explain in 1-2 sentences."
    )
    result = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    explanation = result.choices[0].message.content.strip()
    matches = _extract_yes_no(explanation)
    return {"verdict_matches_ground_truth": matches, "explanation": explanation}


def run_direct_qa_batch(questions: list[dict], out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = []
    correct = 0

    for i, q in enumerate(questions, start=1):
        print(f"\n[{i}/{len(questions)}] ID: {q['source_id']}")
        print(f"Context: {q['problem_context'][:100]}...")

        answer = direct_qa(q["problem_context"], q["candidate_answer"])
        print(f"Answer: {answer[:200]}")

        evaluation = evaluate_direct_qa(answer, q["candidate_answer"], q["ground_truth"])
        matches = evaluation["verdict_matches_ground_truth"]
        if matches:
            correct += 1

        print(f"Correct: {matches}")

        results.append({
            "source_id": q["source_id"],
            "problem_context": q["problem_context"],
            "candidate_answer": q["candidate_answer"],
            "ground_truth": q["ground_truth"],
            "direct_qa_response": answer,
            "evaluation": evaluation,
        })

    accuracy = correct / len(questions) if questions else 0
    print(f"\n{'='*60}")
    print(f"  DIRECT QA RESULTS")
    print(f"{'='*60}")
    print(f"  Questions: {len(questions)}")
    print(f"  Correct:   {correct}")
    print(f"  Accuracy:  {accuracy:.2%}")

    output = {
        "baseline": "direct_qa",
        "model": model,
        "hyperparameters": DEBATE_HYPERPARAMETERS,
        "timestamp": datetime.now().isoformat(),
        "n": len(questions),
        "correct": correct,
        "accuracy": accuracy,
        "results": results,
    }

    path = os.path.join(out_dir, f"direct_qa_{timestamp}.json")
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
        description="Baseline 1: Direct QA with CoT prompting."
    )
    parser.add_argument("--questions-file", type=str, default=None,
                        help="Path to a batch_questions_*.json file to reuse exact questions from a prior debate run.")
    parser.add_argument("--dataset", choices=["strategyqa", "arc"], default="strategyqa",
                        help="Dataset to sample from (ignored if --questions-file is set).")
    parser.add_argument("--n", type=int, default=100,
                        help="Number of questions to sample (ignored if --questions-file is set).")
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

    run_direct_qa_batch(questions, args.out)


if __name__ == "__main__":
    main()
