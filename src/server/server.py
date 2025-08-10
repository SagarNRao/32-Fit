from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
from flask_cors import CORS
from typing import List, Dict

app = Flask(__name__)
CORS(app)

# Load model and encoders
try:
    rf_model = joblib.load('bulkPredictor.pkl')
    le_gender = joblib.load('le_gender.pkl')
    le_exercise = joblib.load('le_exercise.pkl')
    le_experience = joblib.load('le_experience.pkl')
    le_muscle_group = joblib.load('le_muscle_group.pkl')
    le_category = joblib.load('le_category.pkl')
except FileNotFoundError as e:
    print(f"Error loading files: {e}")
    raise

# Baseline muscle growth calculation
def get_baseline_params(age, gender, experience, current_size_cm, workout_time_years):
    base_limit = 45 if gender == 'M' else 30
    age_factor = max(0.7, 1 - (age - 25) * (0.01 if gender == 'M' else 0.008))
    M_max = base_limit * age_factor
    remaining_potential = max(0, M_max - (current_size_cm * 0.2))
    k_base = {'Beginner': 0.20, 'Intermediate': 0.10, 'Advanced': 0.05}
    k = k_base.get(experience, 0.10) * (1 / (1 + workout_time_years * 0.1))
    print(f"Baseline params: M_max={M_max:.2f}, remaining_potential={remaining_potential:.2f}, k={k:.4f}")
    return remaining_potential, k

def calculate_baseline_growth(row, time_months=3, current_size_cm=0, workout_time_years=0):
    M_max, k = get_baseline_params(row['age'], row['gender'], row['experience'], current_size_cm, workout_time_years)
    M0 = current_size_cm * 0.2
    baseline_growth = (M_max - M0) * (1 - np.exp(-k * time_months))
    baseline_cm2 = max(baseline_growth * 5, 0.1)
    print(f"Baseline calc: M0={M0:.2f}, baseline_growth={baseline_growth:.2f}, baseline_cm2={baseline_cm2:.2f}")
    return baseline_cm2

# Safe encoding
def safe_transform(encoder, value, default_value=0):
    try:
        if value in encoder.classes_:
            return encoder.transform([value])[0]
        print(f"Warning: '{value}' not found, using default {default_value}")
        return default_value
    except:
        print(f"Error encoding '{value}', using default {default_value}")
        return default_value

# Prediction function
def predict_multi_exercise_muscle_growth(age: int, gender: str, exercises: List[Dict], frequency: int, 
                                        protein: float, calories: int, sleep: float, experience: str, 
                                        current_size_cm: float = 0, workout_time_years: float = 0, time_months: int = 3) -> List[Dict]:
    try:
        difficulty_weights = {'Compound': 1.0, 'Isolation': 0.8}
        
        # Basic input validation
        if not (18 <= age <= 100) or gender not in le_gender.classes_ or experience not in le_experience.classes_:
            raise ValueError("Invalid age, gender, or experience")
        if not (1 <= frequency <= 7) or not (0 < protein <= 300) or not (0 < calories <= 5000) or not (0 < sleep <= 24):
            raise ValueError("Invalid frequency, protein, calories, or sleep")

        # Group exercises by muscle group
        muscle_groups = {}
        for ex in exercises:
            if not all(key in ex for key in ['exercise_name', 'sets', 'reps', 'weight', 'target_muscle_group', 'exercise_category']):
                raise ValueError("Exercise missing required fields")
            if ex['exercise_name'] not in le_exercise.classes_ or ex['target_muscle_group'] not in le_muscle_group.classes_ or ex['exercise_category'] not in le_category.classes_:
                raise ValueError("Invalid exercise, muscle group, or category")
            if not (1 <= ex['sets'] <= 10) or not (1 <= ex['reps'] <= 20) or not (0 < ex['weight'] <= 300):
                raise ValueError("Invalid sets, reps, or weight")
            
            muscle_group = ex['target_muscle_group']
            muscle_groups.setdefault(muscle_group, []).append(ex)

        results = []
        for muscle_group, ex_list in muscle_groups.items():
            total_volume = 0
            primary_exercise = None
            max_volume = 0
            for ex in ex_list:
                volume = ex['sets'] * ex['reps'] * ex['weight'] * difficulty_weights[ex['exercise_category']]
                total_volume += volume
                if volume > max_volume:
                    max_volume = volume
                    primary_exercise = ex
            print(f"Muscle group: {muscle_group}, total_volume={total_volume:.2f}, primary_exercise={primary_exercise['exercise_name']}")

            # Baseline growth
            baseline = calculate_baseline_growth(
                pd.Series({'age': age, 'gender': gender, 'experience': experience}),
                time_months, current_size_cm, workout_time_years
            )

            # Equivalent exercise metrics
            equiv_sets = min(10, primary_exercise['sets'])
            equiv_reps = min(20, primary_exercise['reps'])
            equiv_weight = min(300, total_volume / (equiv_sets * equiv_reps))
            print(f"Equivalent metrics: sets={equiv_sets}, reps={equiv_reps}, weight={equiv_weight:.2f}")

            # Encode inputs
            gender_encoded = safe_transform(le_gender, gender)
            exercise_encoded = safe_transform(le_exercise, primary_exercise['exercise_name'])
            experience_encoded = safe_transform(le_experience, experience)
            muscle_group_encoded = safe_transform(le_muscle_group, muscle_group)
            category_encoded = safe_transform(le_category, primary_exercise['exercise_category'])
            print(f"Encoded: gender={gender_encoded}, exercise={exercise_encoded}, experience={experience_encoded}, muscle_group={muscle_group_encoded}, category={category_encoded}")

            # Additional features
            protein_per_kg = protein / max(equiv_weight * 0.45, 1)
            volume = equiv_sets * equiv_reps
            intensity = equiv_weight / max(equiv_reps, 1)
            calories_per_kg = calories / max(equiv_weight * 0.45, 1)
            print(f"Features: protein_per_kg={protein_per_kg:.2f}, volume={volume:.2f}, intensity={intensity:.2f}, calories_per_kg={calories_per_kg:.2f}")

            # Model input
            input_data = np.array([[age, gender_encoded, exercise_encoded, equiv_sets, equiv_reps, equiv_weight,
                                   frequency, protein, calories, sleep, experience_encoded,
                                   muscle_group_encoded, category_encoded, protein_per_kg, volume,
                                   intensity, calories_per_kg, 3]])
            print(f"Model input: {input_data}")

            # Predict and adjust
            adjustment = rf_model.predict(input_data)[0]
            adjustment = np.clip(adjustment, 0.01, 10.0)
            adjustment *= min(1.3, 1 + 0.1 * (len(ex_list) - 1))
            print(f"Adjustment: raw={rf_model.predict(input_data)[0]:.4f}, clipped={adjustment:.4f}")

            # Final prediction
            growth = baseline * adjustment
            print(f"Final: baseline={baseline:.2f}, adjustment={adjustment:.4f}, growth={growth:.2f}")
            results.append({
                "muscle_group": muscle_group,
                "growth": round(growth, 2)
            })

        return results or [{"error": "No valid exercises provided"}]

    except Exception as e:
        return [{"error": str(e)}]

# Flask endpoint
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        print("RECIEVED DATA HERE")
        print("RECIEVED DATA HERE")
        print(data)
        print("RECIEVED DATA HERE")
        print("RECIEVED DATA HERE")
        
        
        result = predict_multi_exercise_muscle_growth(
            age=data['age'],
            gender=data['gender'],
            exercises=data['exercises'],
            frequency=data['frequency'],
            protein=data['protein'],
            calories=data['calories'],
            sleep=data['sleep'],
            experience=data['experience'],
            current_size_cm=data.get('current_size_cm', 0),
            workout_time_years=data.get('workout_time_years', 0),
            time_months=data.get('time_months', 3)
        )
        return jsonify({"predictions": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3001)