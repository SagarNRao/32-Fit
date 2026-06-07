"""
FitPredictor API
Serves both /bulk (muscle growth) and /cut (body composition) endpoints.
Models are loaded once at startup from the models/ directory.

Train your models first by running bulk.ipynb and cut.ipynb, which produce:
  bulkPredictor.pkl, le_gender.pkl, le_exercise.pkl, le_experience.pkl,
  le_muscle_group.pkl, le_category.pkl
  models/body_composition_models.pkl, models/le_gender_body.pkl, etc.
"""

import os
import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Load BULK model artifacts
# ---------------------------------------------------------------------------
BULK_DIR = os.environ.get("BULK_MODEL_DIR", ".")
CUT_DIR  = os.environ.get("CUT_MODEL_DIR",  "models")

try:
    rf_bulk         = joblib.load(os.path.join(BULK_DIR, "bulkPredictor.pkl"))
    le_gender_bulk  = joblib.load(os.path.join(BULK_DIR, "le_gender.pkl"))
    le_exercise     = joblib.load(os.path.join(BULK_DIR, "le_exercise.pkl"))
    le_experience_bulk = joblib.load(os.path.join(BULK_DIR, "le_experience.pkl"))
    le_muscle_group = joblib.load(os.path.join(BULK_DIR, "le_muscle_group.pkl"))
    le_category     = joblib.load(os.path.join(BULK_DIR, "le_category.pkl"))
    BULK_LOADED = True
    print("✅ Bulk model loaded")
except Exception as e:
    BULK_LOADED = False
    print(f"⚠️  Bulk model not loaded: {e}")

# ---------------------------------------------------------------------------
# Load CUT model artifacts
# ---------------------------------------------------------------------------
try:
    models_cut           = joblib.load(os.path.join(CUT_DIR, "body_composition_models.pkl"))
    le_gender_cut        = joblib.load(os.path.join(CUT_DIR, "le_gender_body.pkl"))
    le_experience_cut    = joblib.load(os.path.join(CUT_DIR, "le_experience_body.pkl"))
    le_exercise_name_cut = joblib.load(os.path.join(CUT_DIR, "le_exercise_name_body.pkl"))
    le_muscle_group_cut  = joblib.load(os.path.join(CUT_DIR, "le_muscle_group_body.pkl"))
    le_exercise_cat_cut  = joblib.load(os.path.join(CUT_DIR, "le_exercise_category_body.pkl"))
    TIME_INTERVALS       = [3, 6, 9, 12]
    METRICS              = ["bfp", "muscle_mass", "definition"]
    CUT_LOADED = True
    print("✅ Cut model loaded")
except Exception as e:
    CUT_LOADED = False
    print(f"⚠️  Cut model not loaded: {e}")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def safe_transform(encoder, value, default_value=0):
    try:
        if value in encoder.classes_:
            return encoder.transform([value])[0]
        return default_value
    except Exception:
        return default_value


def calculate_baseline_growth(age, gender, experience, current_size_cm, workout_time_years, time_months):
    if gender == "M":
        base_limit = 45
        age_factor = max(0.7, 1 - (age - 25) * 0.01)
    else:
        base_limit = 30
        age_factor = max(0.7, 1 - (age - 25) * 0.008)

    M_max = base_limit * age_factor
    remaining = max(0, M_max - (current_size_cm * 0.2))
    k_base = {"Beginner": 0.20, "Intermediate": 0.10, "Advanced": 0.05}
    k = k_base.get(experience, 0.10) * (1 / (1 + workout_time_years * 0.1))
    M0 = current_size_cm * 0.2
    growth = (remaining - M0) * (1 - np.exp(-k * time_months))
    return max(growth * 5, 0.1)


# ---------------------------------------------------------------------------
# BULK endpoint
# ---------------------------------------------------------------------------
@app.route("/bulk", methods=["POST"])
def bulk_predict():
    if not BULK_LOADED:
        return jsonify({"error": "Bulk model not available"}), 503

    data = request.get_json(force=True)
    age               = data["age"]
    gender            = data["gender"]
    exercises         = data["exercises"]
    frequency         = data["frequency"]
    protein           = data["protein"]
    calories          = data["calories"]
    sleep_hrs         = data["sleep"]
    experience        = data["experience"]
    current_size_cm   = data.get("current_size_cm", 0)
    workout_time_years= data.get("workout_time_years", 0)

    difficulty_weights = {"Compound": 1.0, "Isolation": 0.8}

    # Group by muscle group
    muscle_groups = {}
    for ex in exercises:
        mg = ex["target_muscle_group"]
        muscle_groups.setdefault(mg, []).append(ex)

    result = {}
    for interval in [3, 6, 9, 12]:
        interval_preds = {}
        for muscle_group, ex_list in muscle_groups.items():
            total_volume = 0
            primary = None
            max_vol  = 0
            for ex in ex_list:
                vol = ex["sets"] * ex["reps"] * ex["weight"] * difficulty_weights.get(ex["exercise_category"], 1.0)
                total_volume += vol
                if vol > max_vol:
                    max_vol  = vol
                    primary  = ex

            baseline = calculate_baseline_growth(age, gender, experience, current_size_cm, workout_time_years, interval)

            equiv_sets   = min(10, primary["sets"])
            equiv_reps   = min(20, primary["reps"])
            equiv_weight = min(300, total_volume / (equiv_sets * equiv_reps))

            gender_enc   = safe_transform(le_gender_bulk,    gender)
            ex_enc       = safe_transform(le_exercise,       primary["exercise_name"])
            exp_enc      = safe_transform(le_experience_bulk,experience)
            mg_enc       = safe_transform(le_muscle_group,   muscle_group)
            cat_enc      = safe_transform(le_category,       primary["exercise_category"])

            protein_per_kg  = protein / max(equiv_weight * 0.45, 1)
            volume          = equiv_sets * equiv_reps
            intensity       = equiv_weight / max(equiv_reps, 1)
            calories_per_kg = calories / max(equiv_weight * 0.45, 1)

            input_data = np.array([[
                age, gender_enc, ex_enc, equiv_sets, equiv_reps, equiv_weight,
                frequency, protein, calories, sleep_hrs, exp_enc,
                mg_enc, cat_enc, protein_per_kg, volume,
                intensity, calories_per_kg, 3
            ]])

            adjustment = float(np.clip(rf_bulk.predict(input_data)[0], 0.01, 10.0))
            boost = min(1.3, 1 + 0.1 * (len(ex_list) - 1))
            adjustment *= boost
            prediction = round(baseline * adjustment, 2)
            interval_preds[f"{muscle_group} growth"] = f"{prediction} cm2"

        if interval_preds:
            result[str(interval)] = interval_preds

    return jsonify({"result": result})


# ---------------------------------------------------------------------------
# CUT endpoint
# ---------------------------------------------------------------------------
@app.route("/cut", methods=["POST"])
def cut_predict():
    if not CUT_LOADED:
        return jsonify({"error": "Cut model not available"}), 503

    data = request.get_json(force=True)
    age               = data["age"]
    gender            = data["gender"]
    exercises         = data["exercises"]
    frequency         = data["frequency"]
    protein           = data["protein"]
    calories          = data["calories"]
    sleep_hrs         = data["sleep"]
    experience        = data["experience"]
    genetic_advantage = data.get("genetic_advantage", 3)
    daily_deficit     = data.get("daily_deficit", 500)
    initial_bfp       = data.get("initial_bfp", 20.0)
    current_weight    = data.get("current_weight", 80.0)
    height            = data.get("height", 175.0)

    difficulty_weights = {"Compound": 1.0, "Isolation": 0.8}
    total_volume = 0
    primary = None
    max_vol  = 0

    for ex in exercises:
        vol = ex["sets"] * ex["reps"] * ex["weight"] * difficulty_weights.get(ex.get("exercise_category", "Compound"), 1.0)
        total_volume += vol
        if vol > max_vol:
            max_vol  = vol
            primary  = ex

    equiv_sets   = min(10, primary["sets"])
    equiv_reps   = min(20, primary["reps"])
    equiv_weight = min(300, total_volume / (equiv_sets * equiv_reps))

    # Derived features
    if gender == "M":
        bmr = 88.362 + 13.397 * current_weight + 4.799 * height - 5.677 * age
    else:
        bmr = 447.593 + 9.247 * current_weight + 3.098 * height - 4.330 * age

    bmi             = current_weight / ((height / 100) ** 2)
    activity_level  = frequency * 5
    tdee            = bmr * (1.2 + activity_level * 0.1)
    fat_mass        = (initial_bfp / 100) * current_weight
    muscle_mass     = current_weight - fat_mass
    training_int    = (equiv_weight * equiv_sets * equiv_reps) / current_weight
    sleep_quality   = 1.0 if sleep_hrs >= 7.5 else sleep_hrs / 7.5
    protein_per_kg  = protein / current_weight
    deficit_ratio   = daily_deficit / tdee
    volume          = equiv_sets * equiv_reps * equiv_weight
    intensity       = equiv_weight / max(equiv_reps, 1)
    calories_per_kg = calories / max(current_weight, 1)

    gender_enc  = safe_transform(le_gender_cut,        gender)
    exp_enc     = safe_transform(le_experience_cut,    experience)
    ex_enc      = safe_transform(le_exercise_name_cut, primary["exercise_name"])
    mg_enc      = safe_transform(le_muscle_group_cut,  primary.get("target_muscle_group", "Chest"))
    cat_enc     = safe_transform(le_exercise_cat_cut,  primary.get("exercise_category", "Compound"))

    user_data = np.array([[
        age, gender_enc, current_weight, height, bmi,
        equiv_sets, equiv_reps, equiv_weight, frequency, training_int,
        protein, protein_per_kg, calories, sleep_hrs, sleep_quality,
        exp_enc, genetic_advantage, daily_deficit, deficit_ratio,
        0, initial_bfp, muscle_mass, tdee, activity_level,
        ex_enc, mg_enc, cat_enc, volume, intensity, calories_per_kg
    ]])

    predictions = {}
    for interval in TIME_INTERVALS:
        predictions[str(interval)] = {}
        for metric in METRICS:
            pred = float(models_cut[interval][metric].predict(user_data)[0])
            predictions[str(interval)][metric] = round(max(pred, 0), 2)

    return jsonify({"result": predictions})


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "bulk_model": BULK_LOADED,
        "cut_model":  CUT_LOADED,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3001))
    app.run(host="0.0.0.0", port=port)
