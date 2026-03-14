# dataset_loader.py — Load and format questions from StrategyQA or ARC-Challenge
# for use as debate problem contexts in the pipeline.
#
# Supported datasets:
#   - StrategyQA (Geva et al., 2021): Yes/No questions requiring multi-step reasoning
#       HuggingFace: "wics/strategy-qa"
#   - ARC-Challenge (Clark et al., 2018): Multiple-choice science questions
#       HuggingFace: "allenai/ai2_arc", config "ARC-Challenge"
#
# Usage:
#   python dataset_loader.py --dataset strategyqa --n 100
#   python dataset_loader.py --dataset arc --n 150 --run
#
# Flags:
#   --dataset   strategyqa | arc  (default: strategyqa)
#   --n         number of questions to sample, 100–200  (default: 100)
#   --seed      random seed for reproducible sampling   (default: 42)
#   --run       if set, runs the full debate pipeline on each sampled question
#   --out       output directory for batch transcripts  (default: test_outputs/batch)

import argparse
import json
import os
import random
import sys
from datetime import datetime

from datasets import load_dataset

from config import DEBATE_HYPERPARAMETERS


# ---------------------------------------------------------------------------
# Formatters — convert each dataset's schema into a unified debate dict:
#   {
#     "problem_context": str,   # background + question framing
#     "candidate_answer": str,  # the answer being debated
#     "ground_truth": str,      # correct answer (for Phase 4 evaluation)
#     "source_id": str,         # original question ID for traceability
#   }
# ---------------------------------------------------------------------------

def format_strategyqa(item: dict) -> dict:
    """
    StrategyQA schema:
      - question: str           ("Did Julius Caesar know about the Maya civilization?")
      - answer: bool            (True = Yes, False = No)
      - facts: list[str]        (supporting world-knowledge facts)
      - decomposition: list[str](reasoning steps)

    Debate framing:
      - problem_context: the question + supporting facts as background
      - candidate_answer: the affirmative ("Yes, ...") — Proponent defends this,
        Opponent must argue No. The judge determines which side is correct.
      - ground_truth: the verified Yes/No answer with brief justification from facts.

    Design note: We always frame candidate_answer as the affirmative (Yes) position.
    This means for questions where the answer is No, the correct side is the Opponent.
    The Phase 4 evaluator handles this correctly by comparing against ground_truth.

    Note: In ChilleD/StrategyQA, 'facts' is a single string, not a list.
    """
    question = item["question"]
    answer_bool = item["answer"]
    facts = item.get("facts", "")

    # Build problem context from question + supporting facts
    facts_text = f"\n\nSupporting facts: {facts}" if facts else ""

    problem_context = (
        f"This is a commonsense reasoning question that requires multi-step world knowledge "
        f"to answer correctly. The question is: \"{question}\""
        f"{facts_text}"
    )

    candidate_answer = f"Yes — {question.rstrip('?')}."

    ground_truth = (
        f"{'Yes' if answer_bool else 'No'}. "
        + (f"Supporting evidence: {facts}" if facts else "")
    )

    return {
        "problem_context": problem_context,
        "candidate_answer": candidate_answer,
        "ground_truth": ground_truth,
        "source_id": item.get("qid", "unknown"),
    }


def format_arc(item: dict) -> dict:
    """
    ARC-Challenge schema:
      - question: str
      - choices: {"text": list[str], "label": list[str]}  (A/B/C/D options)
      - answerKey: str   (correct label: "A", "B", "C", or "D")

    Debate framing:
      - problem_context: question stem + all answer choices as background
      - candidate_answer: the correct choice — Proponent defends it,
        Opponent argues for the most plausible distractor.
      - ground_truth: the correct answer label + text.

    Design note: For ARC, we pick the most plausible distractor (the choice
    immediately adjacent to the correct answer in the list) as the implicit
    opposing position, giving the Opponent a reasonable wrong answer to defend.
    """
    question = item["question"]
    choices = item["choices"]
    answer_key = item["answerKey"]

    labels = choices["label"]
    texts = choices["text"]
    choice_map = dict(zip(labels, texts))

    # Format all choices as background context
    choices_text = "\n".join(f"  {lbl}) {txt}" for lbl, txt in zip(labels, texts))
    correct_text = choice_map.get(answer_key, "")

    # Pick the most plausible distractor (first choice that isn't correct)
    distractor_text = next(
        (txt for lbl, txt in zip(labels, texts) if lbl != answer_key),
        "an alternative answer"
    )

    problem_context = (
        f"This is a challenging science reasoning question from ARC-Challenge "
        f"(Clark et al., 2018). Read the question and answer choices carefully.\n\n"
        f"Question: {question}\n\n"
        f"Answer choices:\n{choices_text}\n\n"
        f"The debate concerns whether the correct answer is ({answer_key}) \"{correct_text}\" "
        f"or a plausible alternative such as \"{distractor_text}\"."
    )

    candidate_answer = f"({answer_key}) {correct_text}"

    ground_truth = (
        f"The correct answer is ({answer_key}) \"{correct_text}\". "
        f"The other choices are distractors."
    )

    return {
        "problem_context": problem_context,
        "candidate_answer": candidate_answer,
        "ground_truth": ground_truth,
        "source_id": item.get("id", "unknown"),
    }


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_strategyqa(n: int, seed: int) -> list[dict]:
    """
    Load and sample n questions from StrategyQA.
    Uses the train split (2290 questions) for a large sampling pool.
    """
    print(f"[Loading StrategyQA from HuggingFace...]")
    ds = load_dataset("ChilleD/StrategyQA", split="train")
    items = list(ds)
    random.seed(seed)
    sampled = random.sample(items, min(n, len(items)))
    print(f"[Sampled {len(sampled)} questions from StrategyQA ({len(items)} available)]")
    return [format_strategyqa(item) for item in sampled]


def load_arc(n: int, seed: int) -> list[dict]:
    """
    Load and sample n questions from ARC-Challenge.
    Uses the test split (1172 questions) — the hardest subset.
    """
    print(f"[Loading ARC-Challenge from HuggingFace...]")
    ds = load_dataset("allenai/ai2_arc", "ARC-Challenge", split="test")
    items = list(ds)
    random.seed(seed)
    sampled = random.sample(items, min(n, len(items)))
    print(f"[Sampled {len(sampled)} questions from ARC-Challenge ({len(items)} available)]")
    return [format_arc(item) for item in sampled]


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

class _TeeWriter:
    """Writes to both the terminal and a file simultaneously, preserving streaming."""
    def __init__(self, file):
        self.file = file
        self.terminal = sys.__stdout__

    def write(self, data):
        self.terminal.write(data)
        self.file.write(data)

    def flush(self):
        self.terminal.flush()
        self.file.flush()


def run_batch(questions: list[dict], out_dir: str):
    """
    Run the full debate pipeline on each question.
    Creates a timestamped batch folder containing:
      - q001_<id>.md, q002_<id>.md, ... — one .md per question (full terminal output)
      - batch_questions_<timestamp>.json  — index of all questions used
    Individual transcript JSONs continue saving to test_outputs/ as normal.
    """
    from main import run_debate  # imported here to avoid circular import at module load

    # Create a dedicated folder for this batch run
    batch_ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    batch_dir = os.path.join(out_dir, f"batch_{batch_ts}")       # .md files + batch_questions.json
    json_dir = os.path.join("test_outputs", f"batch_{batch_ts}") # transcript JSONs
    os.makedirs(batch_dir, exist_ok=True)
    os.makedirs(json_dir, exist_ok=True)
    print(f"[Batch folder (.md): {batch_dir}]")
    print(f"[Batch folder (JSON): {json_dir}]")
    print(f"[Hyperparameters: {DEBATE_HYPERPARAMETERS}]")

    results = []
    errors = []

    for i, q in enumerate(questions, start=1):
        # Sanitize source_id for use in filename
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in q["source_id"])[:30]
        md_path = os.path.join(batch_dir, f"q{i:03d}_{safe_id}.md")

        with open(md_path, "w") as md_file:
            # Redirect stdout to tee: terminal + per-question .md file
            sys.stdout = _TeeWriter(md_file)

            try:
                print(f"\n{'=' * 60}")
                print(f"  QUESTION {i} of {len(questions)}  |  ID: {q['source_id']}")
                print(f"{'=' * 60}")

                run_debate(
                    problem_context=q["problem_context"],
                    candidate_answer=q["candidate_answer"],
                    ground_truth=q["ground_truth"],
                    out_dir=json_dir,
                )
                results.append(q)
            except Exception as e:
                errors.append({"index": i, "source_id": q["source_id"], "error": str(e)})
                print(f"\n[ERROR on question {i} ({q['source_id']}): {e}]")
            finally:
                sys.stdout = sys.__stdout__

        print(f"[Saved: {md_path}]")

    # Save the question index for reproducibility
    index_path = os.path.join(
        batch_dir, f"batch_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(index_path, "w") as f:
        json.dump({"hyperparameters": DEBATE_HYPERPARAMETERS, "questions": results, "errors": errors}, f, indent=2)
    print(f"[Batch index saved to {index_path}]")
    if errors:
        print(f"[{len(errors)} question(s) failed: {[e['source_id'] for e in errors]}]")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Load and optionally run debates on StrategyQA or ARC-Challenge questions."
    )
    parser.add_argument(
        "--dataset", choices=["strategyqa", "arc"], default="strategyqa",
        help="Dataset to load: 'strategyqa' (default) or 'arc'"
    )
    parser.add_argument(
        "--n", type=int, default=100,
        help="Number of questions to sample (100–200, default: 100)"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducible sampling (default: 42)"
    )
    parser.add_argument(
        "--run", action="store_true",
        help="If set, run the full debate pipeline on each sampled question"
    )
    parser.add_argument(
        "--out", type=str, default="test_outputs/batch",
        help="Output directory for batch transcripts (default: test_outputs/batch)"
    )
    args = parser.parse_args()

    # Clamp n to 100–200
    n = max(100, min(200, args.n))
    if n != args.n:
        print(f"[Note: n clamped to {n} (valid range: 100–200)]")

    # Load and format questions
    if args.dataset == "strategyqa":
        questions = load_strategyqa(n, args.seed)
    else:
        questions = load_arc(n, args.seed)

    # Preview first 3
    print(f"\n--- Preview (first 3 of {len(questions)}) ---")
    for q in questions[:3]:
        print(f"\nID: {q['source_id']}")
        print(f"Context: {q['problem_context'][:120]}...")
        print(f"Candidate answer: {q['candidate_answer']}")
        print(f"Ground truth: {q['ground_truth']}")

    if args.run:
        run_batch(questions, args.out)
    else:
        print(f"\n[{len(questions)} questions loaded. Use --run to execute the debate pipeline.]")


if __name__ == "__main__":
    main()
