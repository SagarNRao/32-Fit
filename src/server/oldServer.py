from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load models and encoders for bulk.ipynb
try:
    rf_model = joblib.load('bulkPredictor.pkl')
    le_gender = joblib.load('le_gender.pkl')
    le_exercise = joblib.load('le_exercise.pkl')
    le_experience = joblib.load('le_experience.pkl')
    le_muscle_group = joblib.load('le_muscle_group.pkl')
    le_category = joblib.load('le_category.pkl')
except Exception as e:
    print(f"Error loading bulk model or encoders: {str(e)}")
    exit()

# Load models for check.ipynb (assuming similar joblib saving was implemented)
try:
    models = {
        3: {
            'bfp': joblib.load('bfp_model_3.pkl'),
            'muscle_mass': joblib.load('muscle_mass_model_3.pkl'),
            'definition': joblib.load('definition_model_3.pkl')
        },
        6: {
            'bfp': joblib.load('bfp_model_6.pkl'),
            'muscle_mass': joblib.load('muscle_mass_model_6.pkl'),
            'definition': joblib.load('definition_model_6.pkl')
        },
        9: {
            'bfp': joblib.load('bfp_model_9.pkl'),
            'muscle_mass': joblib.load('muscle_mass_model_9.pkl'),
            'definition': joblib.load('definition_model_9.pkl')
        },
        12: {
            'bfp': joblib.load('bfp_model_12.pkl'),
            'muscle_mass': joblib.load('muscle_mass_model_12.pkl'),
            'definition': joblib.load('definition_model_12.pkl')
        }
    }
    # Load encoders for check.ipynb
    le_gender_check = joblib.load('le_gender_check.pkl')
    le_exercise_check = joblib.load('le_exercise_check.pkl')
    le_experience_check = joblib.load('le_experience_check.pkl')
    le_muscle_group_check = joblib.load('le_muscle_group_check.pkl')
    le_category_check = joblib.load('le_category_check.pkl')
except Exception as e:
    print(f"Error loading check model or encoders: {str(e)}")
    exit()

# Helper function for bulk.ipynb baseline growth calculation
def get_baseline_params(age, gender, experience, current_size_cm, workout_time_years):
    if gender == 'M':
        base_limit = 45
        age_factor = max(0.7, 1 - (age - 25) * 0.01)
    else:
        base_limit = 30
        age_factor = max(0.7, 1 - (age - 25) * 0.008)
    
    M_max = base_limit * age_factor
    remaining_potential = max(0, M_max - (current_size_cm * 0.2))
    
    k_base = {'Beginner': 0.20, 'Intermediate': 0.10, 'Advanced': 0.05}
    k = k_base.get(experience, 0.10) * (1 / (1 + workout_time_years * 0.1))
    
    return remaining_potential, k

def calculate_baseline_growth(age, gender, experience, current_size_cm, workout_time_years, time_months):
    M_max, k = get_baseline_params(age, gender, experience, current_size_cm, workout_time_years)
    M0 = current_size_cm * 0.2
    baseline_growth = (M_max - M0) * (1 - np.exp(-k * time_months))
    baseline_cm2 = baseline_growth * 5
    return max(baseline_cm2, 0.1)  # Ensure minimum baseline to avoid division by zero

# Helper function for check.ipynb feature engineering
def calculate_body_composition_features(user_data, gender):
    # Calculate BMR using Mifflin-St Jeor Equation
    if gender == 'M':
        bmr = 88.362 + (13.397 * user_data['current_weight']) + (4.799 * user_data['height']) - (5.677 * user_data['age'])
    else:
        bmr = 447.593 + (9.247 * user_data['current_weight']) + (3.098 * user_data['height']) - (4.330 * user_data['age'])
    
    # BMI
    bmi = user_data['current_weight'] / ((user_data['height'] / 100) ** 2)
    
    # Activity level
    activity_level = user_data['frequency'] * 5
    
    # TDEE
    tdee = bmr * (1.2 + (activity_level * 0.1))
    
    # Estimated fat mass
    estimated_fat_mass = (user_data['BFP'] / 100) * user_data['current_weight']
    
    # Muscle mass
    muscle_mass = user_data['current_weight'] - estimated_fat_mass
    
    # Training intensity
    training_intensity = (user_data['weight'] * user_data['sets'] * user_data['reps']) / user_data['current_weight']
    
    # Sleep quality
    sleep_quality = 1 if user_data['sleep'] >= 7.5 else user_data['sleep'] / 7.5
    
    # Protein per kg
    protein_per_kg = user_data['protein'] / user_data['current_weight']
    
    # Deficit ratio
    deficit_ratio = user_data['daily_deficit'] / tdee
    
    return {
        'BMR': bmr,
        'BMI': bmi,
        'activity_level': activity_level,
        'TDEE': tdee,
        'estimated_fat_mass': estimated_fat_mass,
        'muscle_mass': muscle_mass,
        'training_intensity': training_intensity,
        'sleep_quality': sleep_quality,
        'protein_per_kg': protein_per_kg,
        'deficit_ratio': deficit_ratio
    }

# Endpoint for muscle growth prediction (bulk.ipynb)
@app.route('/predict/bulk', methods=['POST'])
def predict_bulk():
    try:
        data = request.get_json()
        age = data.get('age')
        gender = data.get('gender')
        exercises = data.get('exercises')  # List of {exercise_name, sets, reps, weight}
        frequency = data.get('frequency')
        protein = data.get('protein')
        calories = data.get('calories')
        sleep = data.get('sleep')
        experience = data.get('experience')
        current_size_cm = data.get('current_size_cm', 0)
        workout_time_years = data.get('workout_time_years', 0)
        time_months = data.get('time_months', 3)

        results = []
        for exercise in exercises:
            try:
                # Encode categorical variables
                gender_encoded = le_gender.transform([gender])[0]
                exercise_name_encoded = le_exercise.transform([exercise['exercise_name']])[0]
                muscle_group = next((x for x in pd.read_csv('mostCommonExercises.csv')[['exercise_name', 'target_muscle_group']].values if x[0] == exercise['exercise_name']), [None, 'Chest'])[1]
                muscle_group_encoded = le_muscle_group.transform([muscle_group])[0]
                category = next((x for x in pd.read_csv('mostCommonExercises.csv')[['exercise_name', 'type']].values if x[0] == exercise['exercise_name']), [None, 'Compound'])[1]
                category_encoded = le_category.transform([category])[0]
                experience_encoded = le_experience.transform([experience])[0]

                # Calculate additional features
                weight_kg = exercise['weight'] * 0.453592  # Convert lbs to kg
                protein_per_kg = protein / max(weight_kg, 1)
                volume = exercise['sets'] * exercise['reps']
                intensity = exercise['weight'] / max(exercise['reps'], 1)
                calories_per_kg = calories / max(weight_kg, 1)
                genetic_advantage = data.get('genetic_advantage', 3)  # Default to average

                # Prepare feature array
                features = [
                    age, gender_encoded, exercise_name_encoded, exercise['sets'], exercise['reps'],
                    exercise['weight'], frequency, protein, calories, sleep, experience_encoded,
                    muscle_group_encoded, category_encoded, protein_per_kg, volume, intensity,
                    calories_per_kg, genetic_advantage
                ]

                # Predict adjustment factor
                adjustment_factor = rf_model.predict([features])[0]
                
                # Calculate baseline growth
                baseline_growth = calculate_baseline_growth(
                    age, gender, experience, current_size_cm, workout_time_years, time_months
                )
                
                # Final prediction
                predicted_growth = baseline_growth * adjustment_factor
                
                results.append({
                    'muscle_group': muscle_group,
                    'exercise': exercise['exercise_name'],
                    'predicted_growth_cm2': round(predicted_growth, 2)
                })
            except Exception as e:
                results.append({
                    'muscle_group': muscle_group,
                    'exercise': exercise['exercise_name'],
                    'error': f"Prediction failed: {str(e)}"
                })

        return jsonify({'result': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Endpoint for body composition prediction (check.ipynb)
@app.route('/predict/check', methods=['POST'])
def predict_check():
    try:
        data = request.get_json()
        age = data.get('age')
        gender = data.get('gender')
        exercise_name = data.get('exercise_name')
        sets = data.get('sets')
        reps = data.get('reps')
        weight = data.get('weight')
        frequency = data.get('frequency')
        protein = data.get('protein')
        calories = data.get('calories')
        sleep = data.get('sleep')
        experience = data.get('experience')
        BFP = data.get('BFP')
        daily_deficit = data.get('daily_deficit')
        current_weight = data.get('current_weight')
        height = data.get('height')
        genetic_advantage = data.get('genetic_advantage', 3)
        time_months = data.get('time_months', [3, 6, 9, 12])

        # Encode categorical variables
        gender_encoded = le_gender_check.transform([gender])[0]
        exercise_name_encoded = le_exercise_check.transform([exercise_name])[0]
        muscle_group = next((x for x in pd.read_csv('fatLoss.csv')[['exercise_name', 'target_muscle_group']].values if x[0] == exercise_name), [None, 'Chest'])[1]
        muscle_group_encoded = le_muscle_group_check.transform([muscle_group])[0]
        category = next((x for x in pd.read_csv('fatLoss.csv')[['exercise_name', 'type']].values if x[0] == exercise_name), [None, 'Compound'])[1]
        category_encoded = le_category_check.transform([category])[0]
        experience_encoded = le_experience_check.transform([experience])[0]

        # Calculate body composition features
        user_data = {
            'age': age,
            'current_weight': current_weight,
            'height': height,
            'frequency': frequency,
            'sleep': sleep,
            'protein': protein,
            'daily_deficit': daily_deficit,
            'BFP': BFP,
            'weight': weight,
            'sets': sets,
            'reps': reps
        }
        engineered_features = calculate_body_composition_features(user_data, gender)

        # Prepare feature array
        features = [
            age, gender_encoded, exercise_name_encoded, sets, reps, weight, frequency,
            protein, calories, sleep, experience_encoded, muscle_group_encoded,
            category_encoded, genetic_advantage, engineered_features['BMI'],
            engineered_features['activity_level'], engineered_features['TDEE'],
            engineered_features['estimated_fat_mass'], engineered_features['muscle_mass'],
            engineered_features['training_intensity'], engineered_features['sleep_quality'],
            engineered_features['protein_per_kg'], engineered_features['deficit_ratio']
        ]

        results = {}
        for month in time_months:
            if month not in models:
                continue
            try:
                bfp_pred = models[month]['bfp'].predict([features])[0]
                muscle_mass_pred = models[month]['muscle_mass'].predict([features])[0]
                definition_pred = models[month]['definition'].predict([features])[0]
                
                # Apply constraints
                min_bfp = 3 if gender == 'M' else 8
                bfp_pred = max(bfp_pred, min_bfp)
                definition_pred = min(max(definition_pred, 1), 10)
                
                results[month] = {
                    'bfp': round(bfp_pred, 2),
                    'muscle_mass': round(muscle_mass_pred, 2),
                    'definition': round(definition_pred, 2)
                }
            except Exception as e:
                results[month] = {'error': f"Prediction failed: {str(e)}"}

        return jsonify({'result': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

if __name__ == '__main__':
    app.run(host='localhost', port=3001, debug=False)