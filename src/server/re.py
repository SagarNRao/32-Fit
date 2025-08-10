import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict

# Load the data
try:
    df = pd.read_csv('fatLoss.csv')
    print("Dataset loaded successfully!")
except:
    print("Error loading dataset")
    exit()

print("Dataset Overview:")
print(df.head())
print("\nDataset Info:")
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

# Calculate additional body composition metrics
def calculate_body_composition_features(df):
    """Calculate additional features for body composition prediction"""
    
    # BMI (Body Mass Index)
    df['BMI'] = df['current_weight'] / ((df['height'] / 100) ** 2)
    
    # Estimate muscle mass based on training variables
    # Higher values indicate more muscle mass potential
    df['muscle_mass_index'] = (
        (df['weight'] * df['sets'] * df['reps'] * df['frequency']) / 1000 +  # Training volume
        (df['protein'] / 100) +  # Protein intake factor
        df['genetic_advantage'] +  # Genetic factor
        (df['experience'].map({'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}) * 0.5)  # Experience factor
    )
    
    # Training intensity score
    df['training_intensity'] = (df['weight'] * df['sets'] * df['reps']) / df['current_weight']
    
    # Caloric efficiency (how well deficit matches actual fat loss)
    df['caloric_efficiency'] = df['actual_fat_loss'] / (df['daily_deficit'] / 100)  # Normalize deficit
    
    # Sleep quality factor
    df['sleep_quality'] = np.where(df['sleep'] >= 7.5, 1, df['sleep'] / 7.5)
    
    # Body size indicator (combination of weight and height)
    df['body_size_index'] = (df['current_weight'] * df['height']) / 10000
    
    return df

# Apply body composition calculations
df = calculate_body_composition_features(df)

def predict_body_composition_changes(df):
    """Predict definition and body fat percentage changes"""
    
    # Initialize new columns
    df['predicted_definition'] = 0.0
    df['predicted_body_fat_change'] = 0.0
    df['estimated_current_bf'] = 0.0
    
    # Estimate current body fat percentage based on BMI and other factors
    # This is a simplified estimation - in reality, you'd need more precise measurements
    df['estimated_current_bf'] = np.where(
        df['gender'] == 'M',
        # Male body fat estimation
        np.clip(1.20 * df['BMI'] - 23.13 * (df['muscle_mass_index'] / 10) + 
                16.2 - (df['genetic_advantage'] * 2), 8, 35),
        # Female body fat estimation  
        np.clip(1.48 * df['BMI'] - 18.58 * (df['muscle_mass_index'] / 10) + 
                21.3 - (df['genetic_advantage'] * 2), 12, 40)
    )
    
    # Define thresholds for "high muscle mass" and "big measurements"
    muscle_threshold = df['muscle_mass_index'].quantile(0.7)  # Top 30%
    size_threshold = df['body_size_index'].quantile(0.6)      # Top 40%
    
    # Condition: High muscle mass AND big measurements AND caloric deficit
    high_muscle_condition = (
        (df['muscle_mass_index'] >= muscle_threshold) & 
        (df['body_size_index'] >= size_threshold) & 
        (df['daily_deficit'] > 200)  # Meaningful caloric deficit
    )
    
    # For high muscle mass individuals on deficit
    df.loc[high_muscle_condition, 'predicted_definition'] = np.clip(
        (df.loc[high_muscle_condition, 'actual_fat_loss'] * 0.8) +  # Base definition from fat loss
        (df.loc[high_muscle_condition, 'training_intensity'] / 10) +  # Training contribution
        (df.loc[high_muscle_condition, 'genetic_advantage'] * 0.5) +  # Genetic factor
        np.random.normal(0, 0.5, sum(high_muscle_condition)),  # Some variation
        0, 10
    )
    
    # Body fat percentage decrease for high muscle individuals
    df.loc[high_muscle_condition, 'predicted_body_fat_change'] = -np.clip(
        (df.loc[high_muscle_condition, 'daily_deficit'] / 100) *  # Deficit effect
        (df.loc[high_muscle_condition, 'caloric_efficiency']) *   # Individual efficiency
        (1 + df.loc[high_muscle_condition, 'muscle_mass_index'] / 20),  # Muscle preservation effect
        0.5, 6  # Reasonable range for body fat loss
    )
    
    # For low muscle mass individuals (definition = 0, focus on fat loss only)
    low_muscle_condition = ~high_muscle_condition & (df['daily_deficit'] > 0)
    
    df.loc[low_muscle_condition, 'predicted_definition'] = 0  # No definition without muscle
    
    # Body fat percentage decrease for low muscle individuals (less efficient)
    df.loc[low_muscle_condition, 'predicted_body_fat_change'] = -np.clip(
        (df.loc[low_muscle_condition, 'daily_deficit'] / 150) *  # Less efficient deficit
        (df.loc[low_muscle_condition, 'caloric_efficiency'] * 0.8) *  # Reduced efficiency
        (0.5 + df.loc[low_muscle_condition, 'genetic_advantage'] / 10),  # Genetic help
        0.2, 4  # Lower range for fat loss without muscle
    )
    
    # Calculate final predicted body fat percentage
    df['predicted_final_bf'] = df['estimated_current_bf'] + df['predicted_body_fat_change']
    df['predicted_final_bf'] = np.clip(df['predicted_final_bf'], 5, 45)  # Reasonable bounds
    
    return df

# Apply body composition predictions
df = predict_body_composition_changes(df)

# Create a comprehensive prediction function
def make_body_composition_prediction(
    age, gender, current_weight, height, 
    exercise_name, sets, reps, weight, frequency,
    protein, calories, sleep, experience, genetic_advantage, daily_deficit
):
    """Make a prediction for a new individual"""
    
    # Create input dataframe
    input_data = pd.DataFrame({
        'age': [age],
        'gender': [gender],
        'current_weight': [current_weight],
        'height': [height],
        'exercise_name': [exercise_name],
        'sets': [sets],
        'reps': [reps],
        'weight': [weight],
        'frequency': [frequency],
        'protein': [protein],
        'calories': [calories],
        'sleep': [sleep],
        'experience': [experience],
        'genetic_advantage': [genetic_advantage],
        'daily_deficit': [daily_deficit],
        'actual_fat_loss': [0]  # Placeholder
    })
    
    # Calculate features
    input_data = calculate_body_composition_features(input_data)
    input_data = predict_body_composition_changes(input_data)
    
    return {
        'estimated_current_bf': round(input_data['estimated_current_bf'].iloc[0], 1),
        'predicted_definition': round(input_data['predicted_definition'].iloc[0], 1),
        'predicted_body_fat_change': round(input_data['predicted_body_fat_change'].iloc[0], 1),
        'predicted_final_bf': round(input_data['predicted_final_bf'].iloc[0], 1),
        'muscle_mass_index': round(input_data['muscle_mass_index'].iloc[0], 2),
        'high_muscle_potential': input_data['muscle_mass_index'].iloc[0] >= df['muscle_mass_index'].quantile(0.7)
    }

# Display results and analysis
print("\n" + "="*50)
print("BODY COMPOSITION ANALYSIS RESULTS")
print("="*50)

# Summary statistics
print(f"\nDataset size: {len(df)} individuals")
print(f"\nBody Composition Metrics:")
print(f"Average muscle mass index: {df['muscle_mass_index'].mean():.2f}")
print(f"High muscle mass threshold: {df['muscle_mass_index'].quantile(0.7):.2f}")

print(f"\nDefinition Predictions:")
high_def = df[df['predicted_definition'] > 0]
print(f"Individuals with predicted definition: {len(high_def)} ({len(high_def)/len(df)*100:.1f}%)")
print(f"Average definition score: {high_def['predicted_definition'].mean():.2f}")

print(f"\nBody Fat Changes:")
print(f"Average predicted body fat change: {df['predicted_body_fat_change'].mean():.2f}%")
print(f"Average estimated current body fat: {df['estimated_current_bf'].mean():.1f}%")
print(f"Average predicted final body fat: {df['predicted_final_bf'].mean():.1f}%")

# Example predictions
print("\n" + "="*50)
print("EXAMPLE PREDICTIONS")
print("="*50)

# Example 1: High muscle mass individual
example1 = make_body_composition_prediction(
    age=28, gender='M', current_weight=85, height=180,
    exercise_name='Barbell Bench Press', sets=4, reps=8, weight=100, frequency=4,
    protein=160, calories=2800, sleep=8.0, experience='Advanced', 
    genetic_advantage=4, daily_deficit=400
)

print("\nExample 1 - High Muscle Mass Individual:")
print(f"Estimated current body fat: {example1['estimated_current_bf']}%")
print(f"Predicted definition score: {example1['predicted_definition']}/10")
print(f"Predicted body fat change: {example1['predicted_body_fat_change']}%")
print(f"Predicted final body fat: {example1['predicted_final_bf']}%")
print(f"High muscle potential: {example1['high_muscle_potential']}")

# Example 2: Lower muscle mass individual
example2 = make_body_composition_prediction(
    age=35, gender='F', current_weight=65, height=165,
    exercise_name='Treadmill', sets=1, reps=1, weight=0, frequency=3,
    protein=100, calories=1800, sleep=7.0, experience='Beginner', 
    genetic_advantage=2, daily_deficit=300
)

print("\nExample 2 - Lower Muscle Mass Individual:")
print(f"Estimated current body fat: {example2['estimated_current_bf']}%")
print(f"Predicted definition score: {example2['predicted_definition']}/10")
print(f"Predicted body fat change: {example2['predicted_body_fat_change']}%")
print(f"Predicted final body fat: {example2['predicted_final_bf']}%")
print(f"High muscle potential: {example2['high_muscle_potential']}")

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Plot 1: Muscle Mass Index vs Definition
axes[0,0].scatter(df['muscle_mass_index'], df['predicted_definition'], alpha=0.6)
axes[0,0].set_xlabel('Muscle Mass Index')
axes[0,0].set_ylabel('Predicted Definition Score')
axes[0,0].set_title('Muscle Mass vs Definition Potential')

# Plot 2: Daily Deficit vs Body Fat Change
axes[0,1].scatter(df['daily_deficit'], df['predicted_body_fat_change'], alpha=0.6)
axes[0,1].set_xlabel('Daily Caloric Deficit')
axes[0,1].set_ylabel('Predicted Body Fat Change (%)')
axes[0,1].set_title('Caloric Deficit vs Body Fat Loss')

# Plot 3: Current vs Predicted Body Fat
axes[1,0].scatter(df['estimated_current_bf'], df['predicted_final_bf'], alpha=0.6)
axes[1,0].plot([5, 45], [5, 45], 'r--', label='No change line')
axes[1,0].set_xlabel('Estimated Current Body Fat (%)')
axes[1,0].set_ylabel('Predicted Final Body Fat (%)')
axes[1,0].set_title('Body Fat Transformation')
axes[1,0].legend()

# Plot 4: Definition Distribution
high_muscle = df[df['predicted_definition'] > 0]['predicted_definition']
axes[1,1].hist(high_muscle, bins=20, alpha=0.7, color='blue')
axes[1,1].set_xlabel('Definition Score')
axes[1,1].set_ylabel('Frequency')
axes[1,1].set_title('Distribution of Definition Scores (High Muscle Mass Only)')

plt.tight_layout()
plt.show()

print("\n" + "="*50)
print("KEY INSIGHTS")
print("="*50)
print("• Individuals with high muscle mass and adequate training get definition scores > 0")
print("• Those without significant muscle mass get definition = 0 (focus on fat loss only)")
print("• Body fat percentage decrease depends on caloric deficit, muscle mass, and efficiency")
print("• Higher muscle mass helps preserve muscle during fat loss, leading to better definition")
print("• Genetic advantage and training experience influence both definition and fat loss efficiency")