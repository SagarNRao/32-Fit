# 32-Fit – Muscle Growth Predictor

**32-Fit** is a machine learning side project that predicts realistic muscle size changes during **bulking** (growth) and **cutting** (preservation/loss) phases — to help lifters **trust the process** when visible progress feels slow or uncertain.

## Why this project exists

Building (or keeping) muscle takes serious time and consistency. Without realistic expectations, it's easy to get demotivated and quit too early.  
This tool aims to give data-driven estimates of **how much size you can realistically add** (or how little you might lose) over weeks/months, based on training experience, nutrition setup, recovery, and more.

## How to Run (right now)

1. Go to https://huggingface.co/spaces/sagarNRao/32Fit

OR

2. Clone the repo
   ```bash
   git clone https://github.com/SagarNRao/32-Fit.git

## Approach & Data

Real longitudinal muscle-growth datasets (with controlled training, diet, DEXA scans, etc.) are extremely rare and would take years to collect personally.

So the workflow was:

1. Researched scientific literature and real-world trends on:
   - Natural muscle-building rates by training age (beginner / intermediate / advanced)
   - Impact of surplus/deficit size, protein intake, training volume, sleep, etc.
   - Typical muscle loss/retention patterns during cuts (especially with high protein + resistance training)

2. Used these trends to define realistic growth curves and influencing factors.

3. Asked **Claude** (Anthropic's LLM) to generate **synthetic tabular data** that follows those researched trends and distributions — creating a stand-in dataset large enough for model training.

4. Trained two separate **Random Forest Regressor** models (scikit-learn):
   - One for **bulking** → predicted circumference increase (cm/in) in arms, chest, legs, etc.
   - One for **cutting** → predicted change (loss or retention) under deficit conditions

## Current State

- Models are trained and work (see the `.ipynb` notebooks for training, feature engineering, evaluation).
- Predictions are functional in notebook form.
- No real frontend exists yet — the repo currently contains only Jupyter notebooks (and possibly a minimal `test_server.py` for inference testing).
- Original plan included sprite-based body visualizations (animated physique morphing based on predictions) — but time ran out before implementation.

## Notebooks Overview

- Data generation / synthetic dataset creation
- Exploratory analysis & feature importance
- Model training & hyperparameter tuning (Random Forest)
- Evaluation & prediction examples

