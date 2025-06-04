from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from typing import List, Dict

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load the trained model and label encoders
try:
    model = joblib.load('sizePredictor.pkl')
    le_gender = joblib.load('le_gender.pkl')
    le_exercise = joblib.load('le_exercise.pkl')
    le_experience = joblib.load('le_experience.pkl')
    le_muscle_group = joblib.load('le_muscle_group.pkl')
    le_category = joblib.load('le_category.pkl')
except FileNotFoundError as e:
    raise FileNotFoundError(
        f"Missing .pkl file: {str(e)}. Ensure all .pkl files are in the same directory.")


def predict_multi_exercise_muscle_growth(age: int, gender: str, exercises: List[Dict], frequency: int, protein: float, calories: int, sleep: float, experience: str) -> str:
    try:
        difficulty_weights = {'Compound': 1.0, 'Isolation': 0.8}

        # Validate inputs
        if not (18 <= age <= 100):
            raise ValueError("Age must be between 18 and 100.")
        if gender not in le_gender.classes_:
            raise ValueError(
                f"Gender must be one of {list(le_gender.classes_)}.")
        if experience not in le_experience.classes_:
            raise ValueError(
                f"Experience level must be one of {list(le_experience.classes_)}.")
        if not (1 <= frequency <= 7):
            raise ValueError(
                "Frequency must be between 1 and 7 days per week.")
        if not (0 < protein <= 300):
            raise ValueError("Protein intake must be between 0 and 300 grams.")
        if not (0 < calories <= 5000):
            raise ValueError("Calories must be between 0 and 5000 kcal.")
        if not (0 < sleep <= 24):
            raise ValueError("Sleep must be between 0 and 24 hours.")

        # Group exercises by target muscle group
        muscle_groups = {}
        for ex in exercises:
            if not isinstance(ex, dict):
                raise ValueError(
                    "Each exercise must be a dictionary with exercise_type, sets, reps, weight, target_muscle_group, and exercise_category.")
            if ex['exercise_type'] not in le_exercise.classes_:
                raise ValueError(
                    f"Exercise type must be one of {list(le_exercise.classes_)}.")
            if ex['target_muscle_group'] not in le_muscle_group.classes_:
                raise ValueError(
                    f"Target muscle group must be one of {list(le_muscle_group.classes_)}.")
            if ex['exercise_category'] not in le_category.classes_:
                raise ValueError(
                    f"Exercise category must be one of {list(le_category.classes_)}.")
            if not (1 <= ex['sets'] <= 10):
                raise ValueError("Sets must be between 1 and 10.")
            if not (1 <= ex['reps'] <= 20):
                raise ValueError("Reps must be between 1 and 20.")
            if not (0 < ex['weight'] <= 300):
                raise ValueError("Weight must be between 0 and 300 kg.")

            muscle_group = ex['target_muscle_group']
            if muscle_group not in muscle_groups:
                muscle_groups[muscle_group] = []
            muscle_groups[muscle_group].append(ex)

        # Predict growth for each muscle group
        results = []
        for muscle_group, ex_list in muscle_groups.items():
            total_volume = 0
            primary_exercise = None
            max_volume = 0
            for ex in ex_list:
                volume = ex['sets'] * ex['reps'] * ex['weight'] * \
                    difficulty_weights[ex['exercise_category']]
                total_volume += volume
                if volume > max_volume:
                    max_volume = volume
                    primary_exercise = ex

            equiv_sets = min(10, primary_exercise['sets'])
            equiv_reps = min(20, primary_exercise['reps'])
            equiv_weight = min(300, total_volume / (equiv_sets * equiv_reps))

            gender_encoded = le_gender.transform([gender])[0]
            exercise_encoded = le_exercise.transform(
                [primary_exercise['exercise_type']])[0]
            experience_encoded = le_experience.transform([experience])[0]
            muscle_group_encoded = le_muscle_group.transform([muscle_group])[0]
            category_encoded = le_category.transform(
                [primary_exercise['exercise_category']])[0]

            input_data = np.array([[age, gender_encoded, exercise_encoded, equiv_sets, equiv_reps, equiv_weight,
                                   frequency, protein, calories, sleep, experience_encoded,
                                   muscle_group_encoded, category_encoded]])

            prediction = model.predict(input_data)[0]
            num_exercises = len(ex_list)
            adjustment_factor = 1 + 0.1 * (num_exercises - 1)
            prediction *= min(1.3, adjustment_factor)
            results.append(
                f"{muscle_group} growth: {round(prediction, 2)} cm²")

        return "\n".join(results) if results else "No valid exercises provided."
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        age = data.get('age')
        gender = data.get('gender')
        exercises = data.get('exercises')
        frequency = data.get('frequency')
        protein = data.get('protein')
        calories = data.get('calories')
        sleep = data.get('sleep')
        experience = data.get('experience')
        # target_muscle_group = "Quads"
        
        

        print("AGE: ", age, "GENDER: ", gender, "EXERCISES: ", exercises, "FREQUENCY: ", frequency,
              "PROTEIN: ", protein, "CALORIES: ", calories, "SLEEP: ", sleep, "EXPERIENCE: ", experience)

        if not all([age, gender, exercises, frequency, protein, calories, sleep, experience]):
            return jsonify({'error': 'Missing required fields'}), 400

        result = predict_multi_exercise_muscle_growth(
            age=age,
            gender=gender,
            exercises=exercises,
            frequency=frequency,
            protein=protein,
            calories=calories,
            sleep=sleep,
            experience=experience,
        )

        if "Error" in result:
            return jsonify({'error': result}), 400

        predictions = {}
        for line in result.split("\n"):
            muscle, value = line.split(" growth: ")
            predictions[muscle] = float(value.split(" cm²")[0])

        print(predictions)
        return jsonify({'predictions': predictions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
