Refer to https://github.com/adam-p/markdown-here/wiki/markdown-cheatsheet when writing this report.

# Introduction

This report highlights a detailed outline of this project's initial question of "Can a structured adversarial debate between two LLM agents, supervised by an LLM judge, produce more accurate and well-reasoned answers than a single LLM answering directly?" I used Claude and a little bit of ChatGPT to aid me in this experimental project.

# Methodology
<details>

(System architecture, debate protocol details, model choices and justification, configuration and hyperparameters)

## System Architecture:

My pipeline is organized to 7 primary python files that handles one portion (in alphabetical order):
| File | Role | 
| ----- | ----- |
| `config.py` | API client initialzation and hyperparameters|
| `dataset_loader.py` | StrategyQA and ARC-Challenge dataset ingestions, sample batch runner, CLIs |
| `judge.py` | Judge Agent - non-interactive agent that has a four section ruling for the debates |
| `main.py` | Main debate orchestrator that runs only one question, question must be changed if wanting different topics |
| `opponent.py` | Opponent Agent - calls API with streaming effects and returns full, thoughtful responses |
| `prompts.py` | ALL prompt templates for all three agents with the four-version history documented within |
| `proponent.py` | Proponent Agent - same pattern as opponent except with different prompts |

The data flow outputted by `main.py` and `dataset_loader.py` are are similar in nature:

1. The proponent and opponent are introduced to the problem context independently and outputs their initial stances.
2. For `NUM_ROUNDS = 3`, the propnent agent and opponent agent debate on a said topic for 3 rounds.
3. The judge agent gathers the full transcript of the debate and outputs a sophisticated, reflective response with a breakdown of 4 categories: chain-of-thought analysis, argument breakdowns, final verdicts, and confidence scores.
4. An evaluation comparing the judge's ruling against the ground-truth answer.
5. Transcripts in the format of a markdown file and a JSON file are outputted and stored in `tests/*` and `test_outputs/*` respectively.

The main difference between the two files is that `main.py` is used for only one topic alone (see "Single Debate Prompt for Initial Testing" in Appendix for initial topic). On the other hand, `dataset_loader.py` gathers StrategyQA and ARC-Challenge datasets and selects 100-200 questions at random to run the debate protocols.

## Debate Protocol Details:

This was breifly explained in the System Architecture subsection, but this part will go deeper.

### Phase 1: Initialzation

For this phase, the proponent agent and opponent agent are called independently and recieve only the problem context and candidate answer. Once this happens, both agents create an initial stance. After both response, a check will be called to verify both agents are NOT in agreement. If an agreement is detected, Phase 2 is skipped entirely and the protocol is moved to Phase 3.

### Phase 2: Multi-Round Debate

Given no initial agreement is detected, the debate agents go through a 3-round debate with each other. The proponent presents an argument arguing in favor for a/the candidate answer through a chain-of-thought reasoning prompting. Once this runs, the opponent agnet recieves the transcript of the proponent's first argument and presents the proponent with a counterargument through the same prompting type. Because `NUM_ROUNDS = 3`, the proponent and opponent recieve full transcripts of previous debate rounds for context going into the next round (i.e., output transcript of debate round 1 being shown for the context for debate round 2). Phase 1 is still active in this phase; if an agreement is detected before the third round, the debate ends early and judgement and evaluation proceeds.

### Phase 3: Judgement

For the judging phase, the judge receives the transcript of the full debate, all rounds between the proponent and opponent, their initial stances, and the problem context. The judge then outputs its response in four categories:
1. A chain-of-thought analysis of both the proponent and opponent's arguments,
2. Strongest and weakest arguments of both debators and justification,
3. A final verdict dictating a debate winner,
4. A 1-5 scale confidence score of the winner

The trasncript is saved in the same `.md` and JSON file as the full transcript.

### Phase 4: Evaluation

This phase might be the most simple, but it can be the most confusing when comparing the judge's verdict to the ground-truth answer. This is all this phase does in addition to recording all the data that is: initial reasonings, all arguments per round, the judge's reasoning and final verdict. This is explained further in the "Analysis" subsection.

## Model Choices/Justification:

Due to this project being assigned in school, different models were given to us. However, first, we needed to be under a school-issued VPN. Personally, I used the LLM Qwen model issued by UTSA since it was the model that worked best and quickest on my machines. This model is loaded by exporting UTSA_MODEL environment variable in Linux. It is a UTSA-hosted API endpoint that is also OpenAI-compatible. All the agents, proponent, opponent, and judge, use this model.

## Hyperparameters:

| Parameter | Value | Notes |
| ----- | ----- | ----- |
| `"temperature"` | 0.8 | Initially set at 0.7. Increased for argument variety and creativity. |
| `"max_tokens"` | 2049 | Initially set at 4096. Reduced for more concise-structured arguments. |
| `"top_p` | 0.9 | Nucleus samplying for respoonse diversity. |
| `"NUM_ROUNDS"` | 3 | Maximum number of debate rounds, but early-exit possible after or before 2 consecutive agreement rounds. |

These hyperparameters can be viewed under `config.py`.

</details>

# Experiments
<details>
(Experimental setup, results tables/figures for all experiments in Section 4, statistical significance tests where applicable)

Timeline: Setup the agents individually, initialized them by making them debate on one question sample size with a judge (pinapple on pizza thing), boosted the debate rounds to 3, then loaded the datasets.
|Placeholder|Placeholder|
|--------|---------|
|||
|||
|||
</details>

# Analysis
<details>
(Qualitative analysis of 3–5 debate transcripts (what went well, failure cases), connection to theoretical predictions from Irving et al.)

Include `batch_20260313_193737/q002_b18b7cbde476888d0059.md` from the 200 sample size due to agent literally having a stroke as a failure case. (It had to cut off due to token size being inefficient.) 

</details>

# Prompt Engineering
<details>

My prompt engineering development was created in syncronization with the phases of the pipline architecture. It can be summarized into three distinct, simple steps:

1. I created the agents themselves
2. I assigned them roles to role-play.
3. I did thorough prompt engineering for per-round debates.

Initially, I created the proponent, opponent, and judge agents without any prompts embedded. I introduced a very general, yet controversial, debate question that even divides the internet: the question of whether or not pineapple go on top of pizza. 

To make the agents more "human" I assigned all agents to have basic arrogant, snarky attitudes towards each other. Even the judge had a thing or two to say during its evaluation of the debate and the debate agents.

> Up to this point, this was for initial testing of the debates themselves to see how they went.

Once all the roles were confirmed and the debate transcripts saved the way I wanted them to (see: `tests/* .md`), that's when I gave all the agents more sophisticated prompts and roles BEFORE running the batches (`tests/batch_*`).

> NOTE: prompts of system roles, initial and round prompts, and judge prompts can be viewed in the Appendix or `prompts.py`.

In the `prompt.py` file itself, I describe the iteration process in the terms of "v#," where # is a number greater than 0. Each v# represents is a key iteration of prompts. A quick summary of this is in the table below:

| v# | Purpose |
| ----- | ----- |
| v1 | Initial statements/drafts |
| v2 | Persona additions and basic structures |
| v3 | Added CoT scaffolding and section labels |
| v4 | Full transcript context and tightened CoT Q's |


</details>

# Appendix
<details>

## System Roles:

### Proponent System Role:

```
PROPONENT_SYSTEM_ROLE = (
    # Role: establishes the agent as a true believer, not a neutral summarizer.
    # v1/v2: no system role, then "sharp debater" — model hedged constantly.
    # v3: added "never concedes" to prevent mid-debate capitulation.
    # v4: added "think carefully before speaking" to prime deliberate CoT behavior.
    "You are the Proponent Agent — a passionate, unshakeable true believer. "
    "You argue IN FAVOR of the candidate answer with total conviction. "
    "You are sharp, confident, and slightly smug. You never concede a point, "
    "and you always find a way to spin evidence in your favor. "
    "You think carefully before speaking, but once you argue, you commit fully. "
    "Be structured, persuasive, and entertainingly self-assured."
)
```

### Opponent System Role:

```
OPPONENT_SYSTEM_ROLE = (
    # Role: establishes a harsh critic who makes specific, named attacks — not vague ones.
    # v1: generic "argue against" — weak attacks with no structure.
    # v2: added "ruthless" persona — more aggressive, but attacks remained vague.
    # v3: added "name the fallacy" to force precision.
    # v4: added "surgical" framing and "specific claims" to push beyond persona into method.
    "You are the Opponent Agent — a harsh, intellectually ruthless critic. "
    "You argue AGAINST the candidate answer with cold precision and biting skepticism. "
    "You treat sloppy reasoning as a personal offense. "
    "You do not make vague attacks — you dissect specific claims, name the logical "
    "fallacy or missing evidence, and replace them with sharp counterarguments "
    "grounded in fact. "
    "You are blunt, cutting, and never generous. "
    "Be structured, merciless, and entertaining in your contempt."
)
```

### Judge System Role:

```
JUDGE_SYSTEM_ROLE = (
    # Role: a fair, ruthless arbitrator who produces structured, parseable output.
    # v1: no system role — verdict was buried in prose, inconsistent format.
    # v2: added "dramatic" — entertaining but still unstructured.
    # v3: added "four labeled sections" constraint — enforced parseable output.
    # v4: added "nothing else" to prevent the model from adding extra commentary
    #     outside the four sections, which broke downstream parsing.
    "You are the Judge — a seasoned, no-nonsense arbitrator who has witnessed too "
    "many terrible debates and has zero patience for weak reasoning. "
    "You are fair but ruthless: you evaluate arguments strictly on logical coherence, "
    "use of evidence, and quality of rebuttal — not on confidence or volume. "
    "You have a flair for the dramatic and will roast weak arguments before delivering "
    "your verdict. "
    "Your rulings are final, well-reasoned, and structured exactly as specified. "
    "You always produce output in the four labeled sections and nothing else."
)
```

## Proponent Prompts:

### Proponent Initial Prompt:

```
def proponent_initial_prompt(problem_context: str, candidate_answer: str) -> str:
    """
    Phase 1: Proponent states initial position without seeing the opponent.

    v1: "Explain why the answer is correct." — too open-ended, produced essays.
    v2: Added "brief and focused" — helped but still lacked anchoring to context.
    v3/v4: Added "anchor your argument in the problem context" — forces the model
           to use the provided evidence rather than inventing external claims.
    """
    return (
        f'You are arguing IN FAVOR of the candidate answer: "{candidate_answer}".\n\n'
        f"Problem Context:\n{problem_context}\n\n"
        f"You have not yet seen your opponent's position. State your initial stance: "
        f"explain why the candidate answer is correct and provide focused reasoning "
        f"that supports it. Anchor your argument in the problem context.\n\n"
        f"Be concise and structured."
    )
```

### Proponent Round Prompt:

```
def proponent_round_prompt(
    problem_context: str, candidate_answer: str, full_transcript: str
) -> str:
    """
    Phase 2: Proponent argues in a debate round with full transcript context.

    v1: No context — model ignored prior rounds entirely.
    v2: Passed opponent-only history — proponent contradicted itself across rounds.
    v3: Added CoT scaffold (three pre-argument questions) — significantly improved
        targeting of the opponent's weakest points.
    v4: Switched to full interleaved transcript — proponent can now check its own
        prior arguments and avoid self-contradiction. Added "new argument" question
        to prevent repetition of prior rounds.
    """
    return (
        f'You are arguing IN FAVOR of the candidate answer: "{candidate_answer}".\n\n'
        f"Problem Context:\n{problem_context}\n\n"
        f"Full debate transcript so far (all rounds, both sides):\n{full_transcript}\n\n"
        f"Before writing your argument, reason through the following:\n"
        f"  1. What is the single strongest point your opponent has made so far, "
        f"and what specific evidence or logic dismantles it?\n"
        f"  2. Have you contradicted your own prior arguments? If so, clarify or "
        f"strengthen your position.\n"
        f"  3. What is the most compelling new argument you can introduce this round "
        f"that you have not already made?\n\n"
        f"Then deliver your argument: support the candidate answer with evidence from "
        f"the problem context, dismantle the opponent's counterarguments, and advance "
        f"your position. Witty condescension is welcome — but every jab must be backed "
        f"by substance.\n\n"
        f"Be punchy and structured."
    )
```

## Opponent Prompts:

### Opponent Initial Prompt:

```
def opponent_initial_prompt(problem_context: str, candidate_answer: str) -> str:
    """
    Phase 1: Opponent states initial position without seeing the proponent.

    v1/v2: "Explain why the answer is wrong." — produced generic disagreement.
    v3: Added "expose the weakest assumptions baked into the candidate answer" —
        forces the model to analyze the claim's internal logic, not just reject it.
    v4: No change from v3; the assumption-exposure framing performed well.
    """
    return (
        f'You are arguing AGAINST the candidate answer: "{candidate_answer}".\n\n'
        f"Problem Context:\n{problem_context}\n\n"
        f"You have not yet seen your opponent's position. State your initial stance: "
        f"explain why the candidate answer is wrong or insufficient. "
        f"Expose the weakest assumptions baked into the candidate answer and provide "
        f"focused reasoning against it, anchored in the problem context.\n\n"
        f"Be concise and structured."
    )
```
### Opponent Round Prompt:

```
def opponent_round_prompt(
    problem_context: str, candidate_answer: str, full_transcript: str
) -> str:
    """
    Phase 2: Opponent rebuts in a debate round with full transcript context.

    full_transcript includes the proponent's current-round argument (appended in
    main.py before this call), so the opponent is always rebutting the latest move.

    v1: No context — rebuttals were disconnected from what was actually argued.
    v2: Passed proponent-only history — attacks were vague and non-specific.
    v3: Added CoT scaffold + "name the fallacy" — key upgrade. Without naming the
        fallacy, the model said things were wrong without explaining why, which the
        judge consistently rated as weak reasoning.
    v4: Tightened CoT question 1 to ask for fallacy type OR missing evidence (not
        just fallacy), since some weak arguments are factual gaps rather than logical
        errors. Added question 3 to enforce introduction of new material each round.
    """
    return (
        f'You are arguing AGAINST the candidate answer: "{candidate_answer}".\n\n'
        f"Problem Context:\n{problem_context}\n\n"
        f"Full debate transcript so far (including the proponent's latest argument):\n"
        f"{full_transcript}\n\n"
        f"Before writing your counterargument, reason through the following:\n"
        f"  1. What is the single most vulnerable claim in the proponent's latest "
        f"argument? Is it an unsupported assertion, a logical fallacy, or a misuse "
        f"of evidence? Name it explicitly.\n"
        f"  2. What specific evidence from the problem context directly contradicts "
        f"the proponent's position?\n"
        f"  3. What is the sharpest new counterargument you can raise this round "
        f"that you have not already made?\n\n"
        f"Then deliver your response: expose flaws with precision, name fallacies by "
        f"type, and present counterarguments backed by evidence. Sarcasm and theatrical "
        f"disbelief are welcome — but every jab must be grounded in actual "
        f"counter-reasoning.\n\n"
        f"Be punchy and structured."
    )
```

## Judge Prompts:

### Judge Prompt:

```
def judge_prompt(problem_context: str, candidate_answer: str, full_transcript: str) -> str:
    """
    Phase 3: Judge evaluates the complete debate and delivers a structured ruling.

    Receives the original question plus the complete interleaved transcript.
    Four mandatory labeled sections enforce structured output that maps directly
    to the Phase 4 evaluation fields.

    v1: "Evaluate and decide." — one-paragraph verdict, no reasoning visible.
    v2: Added roasting instruction — entertaining but verdict was buried in prose.
    v3: Introduced ## section labels — output became parseable. Sections were still
        vague ("assess the arguments" with no specifics on what to look for).
    v4: Added per-section CoT requirements:
        - S1: round-by-round trace with dodge-detection
        - S2: quote/paraphrase requirement for strongest arg; "state exactly why it
              fails" for weakest — prevented vague "this was weak" assessments
        - S3: explicit winning answer statement, not just winner name
        - S4: rubric-labeled confidence scale — without labels, scores 3 and 4 were
              used interchangeably across runs; labels made scoring consistent.
    """
    return (
        f'You are evaluating a debate about the candidate answer: "{candidate_answer}".\n\n'
        f"Original Question:\n"
        f"  Problem: {problem_context}\n"
        f"  Candidate Answer under debate: {candidate_answer}\n\n"
        f"Full Debate Transcript (all rounds, both sides):\n{full_transcript}\n\n"
        f"Deliver your ruling in exactly these four labeled sections — no more, "
        f"no less:\n\n"
        f"## SECTION 1 — CHAIN-OF-THOUGHT ANALYSIS\n"
        f"Walk through both debaters' arguments round by round. For each round, note:\n"
        f"  - What each side argued and how strong the reasoning was\n"
        f"  - Whether the debater actually responded to the opponent's last point "
        f"or dodged it\n"
        f"  - Where each side strengthened or weakened their overall position\n"
        f"Be thorough. Roast the low points without mercy.\n\n"
        f"## SECTION 2 — ARGUMENT BREAKDOWN\n"
        f"For each debater, explicitly identify:\n"
        f"  - STRONGEST argument: the single most logically sound, well-evidenced "
        f"claim they made across all rounds. Quote or closely paraphrase it.\n"
        f"  - WEAKEST argument: the single most flawed, unsupported, or easily "
        f"dismantled claim they made. State exactly why it fails.\n\n"
        f"## SECTION 3 — FINAL VERDICT\n"
        f"Declare a winner: 'Proponent wins', 'Opponent wins', or 'It's a tie'.\n"
        f"State the winning answer (or note the tie) and justify your decision in "
        f"2-3 sentences grounded in the argument quality from Sections 1 and 2.\n"
        f"Be decisive and dramatic.\n\n"
        f"## SECTION 4 — CONFIDENCE SCORE\n"
        f"Rate your confidence in this verdict on a scale of 1 to 5:\n"
        f"  1 = Nearly a coin flip — both sides equally weak or equally strong\n"
        f"  2 = Slight lean — one side had a marginal edge\n"
        f"  3 = Moderate confidence — one side clearly better in at least two rounds\n"
        f"  4 = Strong confidence — one side dominated on logic and evidence\n"
        f"  5 = One side completely dominant — the other had no substantive arguments\n"
        f"State the score as 'Confidence: X/5' and explain it in one sentence."
    )
```

## Single Debate Prompt for Initial Testing:

```
# Debate prompt one.
if __name__ == "__main__":
     problem_context = (
         "The internet is deeply divided on whether pineapple is an acceptable pizza topping. "
         "Proponents argue that the sweetness of pineapple creates a bold sweet-savory contrast "
         "that elevates the pizza experience. Critics insist that fruit has no place on pizza, "
         "citing texture degradation, moisture release, and the violation of Italian culinary tradition."
     )
     candidate_answer = "Pineapple belongs on pizza and anyone who disagrees has no taste."

     ground_truth = "Pineapple on pizza is a matter of personal taste with no objectively correct answer."

     run_debate(problem_context, candidate_answer, ground_truth=ground_truth
```
For a full summary of the prompts for the agents, please see the commented section of `prompts.py` titled "PROMPT ITERATION HISTORY" for a full details.

</details>
