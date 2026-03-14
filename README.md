# LLM Debate With Judge-Pipeline

## How to run this code:

> ##### ***NOTICE:***

> **There are two files you can run to experience this code: `main.py` and `dataset_loader.py`.**

> **`main.py` implements just one question in a 3-round debate whereas `dataset_loader.py` gathers a large set of questions, selected at random, to create a sample set of Commonsense Q&A domains through 3-round debates.**
>
---

### **Prerequisites:**

1. Python version used: 3.12.3, so terminal inputs will be `python3`.
2. Run: `pip install openai datasets` inside a Linux terminal.
3. This project requires a user's device to be connected to the UTSA VPN via GlobalConnect OR connected to the UTSA Wi-Fi directly to move onto step 4.
4. To access the servers given for the project, run: `export UTSA_API_KEY='your api key here'`, `export UTSA_BASE_URL='your base URL here'`, and `export UTSA_MODEL='your model here'`.

### **The Single Question Experiment:**

For a single experiment, `main.py` is to be ran as it consists of all the required `.py` files and dependencies compiled into one file. The files and dependancies are listed below:
```
import json
import os
from datetime import datetime

from config import client, model, NUM_ROUNDS
from proponent import proponent_agent, proponent_initial_position
from opponent import opponent_agent, opponent_initial_position
from judge import judge_agent
```

To run `main.py`, you will want to run via Linux terminal: `python3 main.py`.

> Note: Feel free to change the problem_context, candidate_answer, and ground_truth in this file if you want to experiment with different topics!

### **The Batch Run Experiments:**

The batch runs are to be done by running the `dataset_loader.py` file inside a Linux terminal. 

The dependencies for this file are below:
```
import argparse
import json
import os
import random
import sys
from datetime import datetime

from datasets import load_dataset

from config import DEBATE_HYPERPARAMETERS
```

An example run will be `python3 -u dataset_loader.py --dataset strategyqa --n 200 --seed 99 --run --out tests | tee tests/batch_run_$(date +%Y%m%d_%H%M%S).md`.

Here is a rundown of what each flag does:

| Flag  | Description |
| ------------- | ------------- |
| `-u` | This forces the output to be **unbuffered**. This will create a "streaming" effect while Python prints the output in real time. |
| `--dataset`  | `strategyqa` or `arc`  |
| `--n`  | Number of questions to sample (in this project, the number of sample sets was 100-200)  |
| `--seed` | Random seeds for reproductible sampling (default: 42) |
| `--run` | Executes the pipeline; omit to just preview questions WITHOUT running pipeline |
| `--out` | Where to save the `.md` files and `batch_questions.json` (my cases used `tests/`) |

### **Output Locations:**

For JSON files, go to `test_outputs/batch_*/`, and terminal outputs go to `tests/batch_*/`.

### **Runtime:**

Approximately  3 minutes and 46 seconds per question, so 100 questions ≈ 6-7hrs whereas 200 questions ≈ 12-13hrs. This time will fluctuate depending on how many samples you want to test.
