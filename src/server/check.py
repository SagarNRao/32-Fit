# Body Composition Analysis - Complete Implementation with Exercise Support
# This notebook implements Random Forest Regressor models to predict BFP changes, muscle mass changes, 
# and definition scores at different time intervals (3, 6, 9, 12 months) while considering exercises.

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
import joblib

# Load the data
try:
    df = pd.read_csv('fatLoss.csv')
    print('Dataset loaded successfully!')
except:
    print('Error loading dataset')
    exit()

print('Dataset Overview:')
print(df.head())
print('\nDataset Info:')
print(df.info())

# Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
df.loc[df['gender'] == 'M', 'BMR'] = (
    88.362
    + (13.397 * df.loc[df['gender'] == 'M', 'current_weight'])
    + (4.799 * df.loc[df['gender'] == 'M', 'height'])
    - (5.677 * df.loc[df['gender'] == 'M', 'age'])
)

df.loc[df['gender'] == 'F', 'BMR'] = (
    447.593
    + (9.247 * df.loc[df['gender'] == 'F', 'current_weight'])
    + (3.098 * df.loc[df['gender'] == 'F', 'height'])
    - (4.330 * df.loc[df['gender'] == 'F', 'age'])
)

# Generate initial BFP if not present
np.random.seed(42)  # For reproducibility
df['BFP'] = np.random.uniform(5, 50, size=len(df))

# Add exercise-related columns if they don't exist (simulate exercise data for fat loss dataset)
if 'exercise_name' not in df.columns:
    exercise_names = ['Barbell Bench Press', 'Barbell Rows', 'Squats', 'Deadlifts', 'Pull-ups', 
                     'Dumbbell Press', 'Lat Pulldowns', 'Bicep Curls', 'Tricep Extensions', 'Leg Press']
    df['exercise_name'] = np.random.choice(exercise_names, size=len(df))

if 'target_muscle_group' not in df.columns:
    muscle_groups = ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms']
    df['target_muscle_group'] = np.random.choice(muscle_groups, size=len(df))

# Add exercise category if not present
if 'exercise_category' not in df.columns:
    compound_exercises = ['Barbell Bench Press', 'Barbell Rows', 'Squats', 'Deadlifts', 'Pull-ups', 'Lat Pulldowns']
    df['exercise_category'] = df['exercise_name'].apply(
        lambda x: 'Compound' if x in compound_exercises else 'Isolation'
    )

print('BMR, BFP, and exercise data prepared!')

# Feature Engineering - Calculate body composition metrics
def calculate_body_composition_features(df):
    """Calculate additional features for body composition prediction"""
    
    # BMI (Body Mass Index)
    df['BMI'] = df['current_weight'] / ((df['height'] / 100) ** 2)
    
    # Activity level (using 5 as default intensity)
    df['activity_level'] = df['frequency'] * 5
    
    # TDEE (Total Daily Energy Expenditure)
    df['TDEE'] = df['BMR'] * (1.2 + (df['activity_level'] * 0.1))
    
    # Estimated fat mass
    df['estimated_fat_mass'] = (df['BFP'] / 100) * df['current_weight']
    
    # Estimate muscle mass
    df['muscle_mass'] = df['current_weight'] - df['estimated_fat_mass']
    
    # Training intensity score
    df['training_intensity'] = (df['weight'] * df['sets'] * df['reps']) / df['current_weight']
    
    # Sleep quality factor
    df['sleep_quality'] = np.where(df['sleep'] >= 7.5, 1, df['sleep'] / 7.5)
    
    # Protein per kg body weight
    df['protein_per_kg'] = df['protein'] / df['current_weight']
    
    # Caloric deficit ratio
    df['deficit_ratio'] = df['daily_deficit'] / df['TDEE']
    
    # Volume calculation (same as bulk.ipynb)
    df['volume'] = df['sets'] * df['reps'] * df['weight']
    
    # Exercise-related features
    df['intensity'] = df['weight'] / np.maximum(df['reps'], 1)
    df['calories_per_kg'] = df['calories'] / np.maximum(df['current_weight'], 1)
    
    return df

# Apply feature engineering
df = calculate_body_composition_features(df)
print('Feature engineering completed!')

# Handle categorical variables
le_gender = LabelEncoder()
le_experience = LabelEncoder()
le_type = LabelEncoder()
le_exercise_name = LabelEncoder()
le_muscle_group = LabelEncoder()
le_exercise_category = LabelEncoder()

df['gender_encoded'] = le_gender.fit_transform(df['gender'])
df['experience_encoded'] = le_experience.fit_transform(df['experience'])
df['type_encoded'] = le_type.fit_transform(df['type'])
df['exercise_name_encoded'] = le_exercise_name.fit_transform(df['exercise_name'])
df['muscle_group_encoded'] = le_muscle_group.fit_transform(df['target_muscle_group'])
df['exercise_category_encoded'] = le_exercise_category.fit_transform(df['exercise_category'])

# Generate target variables for BFP and muscle mass at different time intervals
np.random.seed(42)

# Calculate predicted weight after fat loss
df['predicted_weight_after_loss'] = df['current_weight'] - df['actual_fat_loss']

# Generate BFP at different months (decreasing over time)
# More aggressive fat loss in early months, slower later
df['bfp_at_3'] = df['BFP'] - np.random.uniform(2, 5, size=len(df))
df['bfp_at_6'] = df['bfp_at_3'] - np.random.uniform(1, 3, size=len(df))
df['bfp_at_9'] = df['bfp_at_6'] - np.random.uniform(0.5, 2, size=len(df))
df['bfp_at_12'] = df['bfp_at_9'] - np.random.uniform(0.5, 1.5, size=len(df))

# Ensure BFP doesn't go below realistic minimum (3% for men, 8% for women)
min_bfp = np.where(df['gender'] == 'M', 3, 8)
df['bfp_at_3'] = np.maximum(df['bfp_at_3'], min_bfp)
df['bfp_at_6'] = np.maximum(df['bfp_at_6'], min_bfp)
df['bfp_at_9'] = np.maximum(df['bfp_at_9'], min_bfp)
df['bfp_at_12'] = np.maximum(df['bfp_at_12'], min_bfp)

# Calculate muscle mass at different time intervals
# Assuming some muscle gain due to training
muscle_gain_factor = 1 + (df['training_intensity'] * 0.001)  # Small muscle gain

df['muscle_mass_at_3'] = (df['predicted_weight_after_loss'] * (1 - df['bfp_at_3']/100)) * muscle_gain_factor
df['muscle_mass_at_6'] = (df['predicted_weight_after_loss'] * (1 - df['bfp_at_6']/100)) * muscle_gain_factor
df['muscle_mass_at_9'] = (df['predicted_weight_after_loss'] * (1 - df['bfp_at_9']/100)) * muscle_gain_factor
df['muscle_mass_at_12'] = (df['predicted_weight_after_loss'] * (1 - df['bfp_at_12']/100)) * muscle_gain_factor

# Calculate definition scores (higher muscle mass + lower BFP = higher definition)
# Scale to 1-10 range
def calculate_definition(muscle_mass, bfp):
    # Higher muscle mass and lower BFP = better definition
    definition_raw = (muscle_mass / 10) * (50 - bfp) / 10
    # Scale to 1-10 range
    return np.clip(definition_raw / definition_raw.max() * 9 + 1, 1, 10)

df['definition_at_3'] = calculate_definition(df['muscle_mass_at_3'], df['bfp_at_3'])
df['definition_at_6'] = calculate_definition(df['muscle_mass_at_6'], df['bfp_at_6'])
df['definition_at_9'] = calculate_definition(df['muscle_mass_at_9'], df['bfp_at_9'])
df['definition_at_12'] = calculate_definition(df['muscle_mass_at_12'], df['bfp_at_12'])

print('Target variables generated for all time intervals!')
print(f'BFP range at 12 months: {df["bfp_at_12"].min():.1f}% - {df["bfp_at_12"].max():.1f}%')
print(f'Definition score range at 12 months: {df["definition_at_12"].min():.1f} - {df["definition_at_12"].max():.1f}')

# Define enhanced feature set including exercise features
features = [
    'age', 'gender_encoded', 'current_weight', 'height', 'BMI',
    'sets', 'reps', 'weight', 'frequency', 'training_intensity',
    'protein', 'protein_per_kg', 'calories', 'sleep', 'sleep_quality',
    'experience_encoded', 'genetic_advantage', 'daily_deficit', 'deficit_ratio',
    'type_encoded', 'BFP', 'muscle_mass', 'TDEE', 'activity_level', 
    'exercise_name_encoded', 'muscle_group_encoded', 'exercise_category_encoded',
    'volume', 'intensity', 'calories_per_kg'
]

# Check if all features exist
missing_features = [f for f in features if f not in df.columns]
if missing_features:
    print(f"Missing features: {missing_features}")
else:
    X = df[features]
    print(f"Feature matrix prepared with {len(features)} features")
    print(f"Dataset shape: {X.shape}")

# Train Random Forest models for each time interval and metric
time_intervals = [3, 6, 9, 12]
metrics = ['bfp', 'muscle_mass', 'definition']

# Dictionary to store all models
models = {}
model_scores = {}

# Train models for each combination
for interval in time_intervals:
    models[interval] = {}
    model_scores[interval] = {}
    
    for metric in metrics:
        target_col = f'{metric}_at_{interval}'
        y = df[target_col]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Random Forest model
        rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        rf.fit(X_train, y_train)
        
        # Make predictions and evaluate
        y_pred = rf.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Store model and scores
        models[interval][metric] = rf
        model_scores[interval][metric] = {'mse': mse, 'r2': r2}
        
        print(f'{metric.upper()} at {interval} months - MSE: {mse:.3f}, R²: {r2:.3f}')

print('\nAll models trained successfully!')

# Function to safely encode new data (same as bulk.ipynb)
def safe_transform(encoder, value, default_value=0):
    """Safely transform a value using a label encoder, returning default if not found"""
    try:
        if value in encoder.classes_:
            return encoder.transform([value])[0]
        else:
            print(f"Warning: '{value}' not found in training data, using default")
            return default_value
    except:
        return default_value

# Enhanced prediction function for multiple exercises (adapted from bulk.ipynb approach)
def predict_body_composition_journey_with_exercises(age: int, gender: str, exercises: List[Dict], 
                                                  frequency: int, protein: float, calories: int, 
                                                  sleep: float, experience: str, genetic_advantage: int = 3,
                                                  daily_deficit: float = 500, initial_bfp: float = 20.0,
                                                  current_weight: float = 80.0, height: float = 180.0):
    """
    Predict complete body composition journey for a new user with multiple exercises
    Returns predictions for BFP, muscle mass, and definition at 3, 6, 9, 12 months
    """
    
    try:
        # Define difficulty weights based on exercise category (same as bulk.ipynb)
        difficulty_weights = {
            'Compound': 1.0,
            'Isolation': 0.8
        }
        
        # Calculate total volume and get primary exercise characteristics
        total_volume = 0
        primary_exercise = None
        max_volume = 0
        
        for ex in exercises:
            volume = ex['sets'] * ex['reps'] * ex['weight'] * difficulty_weights.get(ex.get('exercise_category', 'Compound'), 1.0)
            total_volume += volume
            if volume > max_volume:
                max_volume = volume
                primary_exercise = ex
        
        # Convert total volume to equivalent sets, reps, weight (same logic as bulk.ipynb)
        equiv_sets = min(10, primary_exercise['sets'])
        equiv_reps = min(20, primary_exercise['reps'])
        equiv_weight = min(300, total_volume / (equiv_sets * equiv_reps))
        
        # Calculate BMR
        if gender == 'M':
            bmr = (88.362 + (13.397 * current_weight) + 
                   (4.799 * height) - (5.677 * age))
        else:
            bmr = (447.593 + (9.247 * current_weight) + 
                   (3.098 * height) - (4.330 * age))
        
        # Calculate derived features
        bmi = current_weight / ((height / 100) ** 2)
        activity_level = frequency * 5
        tdee = bmr * (1.2 + (activity_level * 0.1))
        estimated_fat_mass = (initial_bfp / 100) * current_weight
        muscle_mass = current_weight - estimated_fat_mass
        training_intensity = (equiv_weight * equiv_sets * equiv_reps) / current_weight
        sleep_quality = 1 if sleep >= 7.5 else sleep / 7.5
        protein_per_kg = protein / current_weight
        deficit_ratio = daily_deficit / tdee
        volume = equiv_sets * equiv_reps * equiv_weight
        intensity = equiv_weight / max(equiv_reps, 1)
        calories_per_kg = calories / max(current_weight, 1)
        
        # Encode categorical variables
        gender_encoded = safe_transform(le_gender, gender)
        experience_encoded = safe_transform(le_experience, experience)
        exercise_name_encoded = safe_transform(le_exercise_name, primary_exercise['exercise_name'])
        muscle_group_encoded = safe_transform(le_muscle_group, primary_exercise.get('target_muscle_group', 'Chest'))
        exercise_category_encoded = safe_transform(le_exercise_category, primary_exercise.get('exercise_category', 'Compound'))
        
        # Use default for 'type' since it's not provided in the exercise data
        type_encoded = 0  # Default value
        
        # Create input array
        user_data = np.array([[
            age, gender_encoded, current_weight, height, bmi,
            equiv_sets, equiv_reps, equiv_weight, frequency, training_intensity,
            protein, protein_per_kg, calories, sleep, sleep_quality,
            experience_encoded, genetic_advantage, daily_deficit, deficit_ratio,
            type_encoded, initial_bfp, muscle_mass, tdee, activity_level,
            exercise_name_encoded, muscle_group_encoded, exercise_category_encoded,
            volume, intensity, calories_per_kg
        ]])
        
        # Make predictions for all time intervals
        predictions = {}
        
        for interval in time_intervals:
            predictions[interval] = {}
            
            for metric in metrics:
                pred = models[interval][metric].predict(user_data)[0]
                predictions[interval][metric] = max(pred, 0)  # Ensure non-negative values
        
        return predictions
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        return None

# Example usage with multiple exercises
exercises = [
    {
        'exercise_name': 'Barbell Bench Press',
        'sets': 4,
        'reps': 10,
        'weight': 80,
        'target_muscle_group': 'Chest',
        'exercise_category': 'Compound'
    },
    {
        'exercise_name': 'Barbell Rows',
        'sets': 4,
        'reps': 10,
        'weight': 75,
        'target_muscle_group': 'Back',
        'exercise_category': 'Compound'
    },
    {
        'exercise_name': 'Squats',
        'sets': 4,
        'reps': 12,
        'weight': 100,
        'target_muscle_group': 'Legs',
        'exercise_category': 'Compound'
    }
]

# Test the enhanced prediction function
journey = predict_body_composition_journey_with_exercises(
    age=28,
    gender='M',
    exercises=exercises,
    frequency=4,
    protein=150,
    calories=2200,
    sleep=8.0,
    experience='Intermediate',
    genetic_advantage=4,
    daily_deficit=500,
    initial_bfp=18.0,
    current_weight=85.0,
    height=180.0
)

# Display results
if journey:
    print('\n=== BODY COMPOSITION JOURNEY PREDICTION WITH EXERCISES ===')
    print(f'Starting Stats: Weight: 85kg, BFP: 18.0%')
    print(f'Workout: {len(exercises)} exercises with total volume focus')
    print('\nPredicted Progress:')

    for interval in time_intervals:
        print(f'\nMonth {interval}:')
        print(f'  Body Fat: {journey[interval]["bfp"]:.1f}%')
        print(f'  Muscle Mass: {journey[interval]["muscle_mass"]:.1f}kg')
        print(f'  Definition Score: {journey[interval]["definition"]:.1f}/10')

# Save all models and encoders
joblib.dump(models, 'body_composition_models.pkl')
joblib.dump(le_gender, 'le_gender_body.pkl')
joblib.dump(le_experience, 'le_experience_body.pkl')
joblib.dump(le_exercise_name, 'le_exercise_name_body.pkl')
joblib.dump(le_muscle_group, 'le_muscle_group_body.pkl')
joblib.dump(le_exercise_category, 'le_exercise_category_body.pkl')

print('\nModels and encoders saved successfully!')
print(f'Available exercises: {len(le_exercise_name.classes_)}')
print(f'Available muscle groups: {len(le_muscle_group.classes_)}')