# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a course archive repository for CS 6263 Spring 2026 - Natural Language Processing with Large Language Models. It serves as storage for Python code and projects developed during the course.

## Repository Structure

- `coding-w-agents/`: Contains projects and code related to coding with AI agents
  - `detectron2/`: Facebook AI Research's computer vision library (included as course material/reference)
- Root-level Python files and Jupyter notebooks will contain NLP course assignments and projects

## Working with Detectron2 (in coding-w-agents/)

When working in the `coding-w-agents/detectron2/` directory:

### Setup and Installation
```bash
cd coding-w-agents/detectron2
python -m pip install -e .
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_config.py
```

### Training Models
```bash
# Basic training command
python tools/train_net.py --config-file configs/COCO-Detection/retinanet_R_50_FPN_1x.yaml

# Multi-GPU training
python tools/train_net.py --num-gpus 8 --config-file configs/COCO-Detection/retinanet_R_50_FPN_1x.yaml
```

### Running Inference/Demo
```bash
# Run demo on images
python demo/demo.py --config-file configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
  --input input.jpg --opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl
```

## Git Workflow

This is an educational repository tracking coursework. When committing:
- Use descriptive commit messages that reference the assignment or topic
- Organize code by topic/assignment in appropriately named directories
- Keep the main branch clean and organized

## Architecture Notes

### Detectron2 Architecture
- **Config System**: Uses YAML configs in `configs/` or LazyConfig in Python files
- **Model Zoo**: Pre-trained models organized by task (detection, segmentation, keypoints, panoptic)
- **Core Components**:
  - `detectron2/modeling/`: Model architectures (backbone, FPN, heads)
  - `detectron2/data/`: Dataset registration, data loaders, transforms
  - `detectron2/engine/`: Training loops, hooks, and defaults
  - `detectron2/config/`: Configuration management
  - `detectron2/evaluation/`: Evaluation metrics for different tasks

### Key Patterns
- Models are built using the config system and registered components
- Custom models/datasets extend base classes and register with the registry system
- Training uses the `DefaultTrainer` class or custom trainers inheriting from `TrainerBase`
