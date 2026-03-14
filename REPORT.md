Refer to https://github.com/adam-p/markdown-here/wiki/markdown-cheatsheet when writing this report.

# Introduction

This report highlights a detailed outline of this project's initial question of "Can a structured adversarial debate between two LLM agents, supervised by an LLM judge, produce more accurate and well-reasoned answers than a single LLM answering directly?" I used Claude and a little bit of ChatGPT to aid me in this experimental project.

# Methodology

(System architecture, debate protocol details, model choices and justification, configuration and hyperparameters)

# Experiments

(Experimental setup, results tables/figures for all experiments in Section 4, statistical significance tests where applicable)

Timeline: Setup the agents individually, initialized them by making them debate on one question sample size with a judge (pinapple on pizza thing), boosted the debate rounds to 3, then loaded the datasets.

# Analysis
(Qualitative analysis of 3–5 debate transcripts (what went well, failure cases), connection to theoretical predictions from Irving et al.)

Include `batch_20260313_193737/q002_b18b7cbde476888d0059.md` from the 200 sample size due to agent literally having a stroke as a failure case. (It had to cut off due to token size being inefficient.) 

# Prompt Engineering

(Describe your prompt design process: how you crafted and iterated prompts for Debater A, Debater B, and the Judge. Explain key design decisions (role framing, CoT instructions, output format constraints) and what changed between iterations based on failure analysis)

1. I created the agents themselves
2. I assigned them roles to role-play.
3. I did thorough  prompt engineering then.

# Appendix
(nclude the complete, final prompt templates for all three agents (Debater A, Debater B, Judge). Present each prompt verbatim with variable placeholders clearly marked. Use Markdown code blocks or collapsible <details> sections for readability)
