import pandas as pd
import numpy as np
import gradio as gr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from typing import List, Dict
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  SHARED EXERCISE LIST
# ─────────────────────────────────────────────
EXERCISES = [
    '21s','Barbell Bench Press','Barbell Curls','Barbell Rows','Cable Crossover',
    'Cable Curls','Chest Dips','Chin-ups','Close Grip Lat Pulldowns',
    'Concentration Curls','Deadlifts','Decline Barbell Bench Press',
    'Decline Dumbbell Press','Dumbbell Bench Press','Dumbbell Curls',
    'Dumbbell Flyes','Dumbbell Rows','Face Pulls','Good Mornings',
    'Hammer Curls','Hyperextensions','Incline Barbell Bench Press',
    'Incline Dumbbell Flyes','Incline Dumbbell Press','Lat Pulldowns',
    'Machine Chest Press','Pec Deck Machine','Preacher Curls','Pull-ups',
    'Push-ups','Rack Pulls','Reverse Flyes','Romanian Deadlifts',
    'Seated Cable Rows','Shrugs','Sumo Deadlifts','T-Bar Rows',
    'Upright Rows','Wide Grip Lat Pulldowns'
]
MUSCLE_GROUPS = ['Back', 'Biceps', 'Chest', 'Traps']
EX_TYPES      = ['Compound', 'Isolation']
EXPERIENCE    = ['Beginner', 'Intermediate', 'Advanced']
GENDERS       = ['M', 'F']

EXERCISE_TO_MUSCLE = {
    'Barbell Bench Press':'Chest','Dumbbell Bench Press':'Chest',
    'Incline Barbell Bench Press':'Chest','Incline Dumbbell Press':'Chest',
    'Decline Barbell Bench Press':'Chest','Decline Dumbbell Press':'Chest',
    'Cable Crossover':'Chest','Chest Dips':'Chest','Dumbbell Flyes':'Chest',
    'Incline Dumbbell Flyes':'Chest','Machine Chest Press':'Chest','Pec Deck Machine':'Chest',
    'Push-ups':'Chest',
    'Barbell Curls':'Biceps','Dumbbell Curls':'Biceps','Cable Curls':'Biceps',
    'Chin-ups':'Biceps','Concentration Curls':'Biceps','Hammer Curls':'Biceps',
    'Preacher Curls':'Biceps','21s':'Biceps',
    'Barbell Rows':'Back','Deadlifts':'Back','Lat Pulldowns':'Back',
    'Pull-ups':'Back','Seated Cable Rows':'Back','T-Bar Rows':'Back',
    'Wide Grip Lat Pulldowns':'Back','Close Grip Lat Pulldowns':'Back',
    'Dumbbell Rows':'Back','Good Mornings':'Back','Hyperextensions':'Back',
    'Romanian Deadlifts':'Back','Rack Pulls':'Back',
    'Shrugs':'Traps','Upright Rows':'Traps','Face Pulls':'Traps',
    'Reverse Flyes':'Traps','Sumo Deadlifts':'Traps',
}
EXERCISE_TO_TYPE = {
    'Barbell Bench Press':'Compound','Barbell Rows':'Compound','Deadlifts':'Compound',
    'Lat Pulldowns':'Compound','Pull-ups':'Compound','Chin-ups':'Compound',
    'Squats':'Compound','T-Bar Rows':'Compound','Seated Cable Rows':'Compound',
    'Dumbbell Rows':'Compound','Incline Barbell Bench Press':'Compound',
    'Dumbbell Bench Press':'Compound','Decline Barbell Bench Press':'Compound',
    'Romanian Deadlifts':'Compound','Sumo Deadlifts':'Compound','Rack Pulls':'Compound',
    'Good Mornings':'Compound','Hyperextensions':'Compound','Chest Dips':'Compound',
    'Push-ups':'Compound','Wide Grip Lat Pulldowns':'Compound',
    'Close Grip Lat Pulldowns':'Compound','Upright Rows':'Compound',
}

def get_type(ex): return EXERCISE_TO_TYPE.get(ex, 'Isolation')
def get_muscle(ex): return EXERCISE_TO_MUSCLE.get(ex, 'Chest')

# ─────────────────────────────────────────────
#  BULK MODEL TRAINING
# ─────────────────────────────────────────────
print("Training Bulk model…")
bulk_df = pd.read_csv("mostCommonExercises.csv")

le_b_gender   = LabelEncoder().fit(bulk_df['gender'])
le_b_exercise = LabelEncoder().fit(bulk_df['exercise_name'])
le_b_muscle   = LabelEncoder().fit(bulk_df['target_muscle_group'])
le_b_category = LabelEncoder().fit(bulk_df['type'])
le_b_exp      = LabelEncoder().fit(bulk_df['experience'])

bulk_df['gender_encoded']        = le_b_gender.transform(bulk_df['gender'])
bulk_df['exercise_name_encoded'] = le_b_exercise.transform(bulk_df['exercise_name'])
bulk_df['muscle_group_encoded']  = le_b_muscle.transform(bulk_df['target_muscle_group'])
bulk_df['category_encoded']      = le_b_category.transform(bulk_df['type'])
bulk_df['experience_encoded']    = le_b_exp.transform(bulk_df['experience'])
bulk_df['protein_per_kg']        = bulk_df['protein'] / np.maximum(bulk_df['weight'] * 0.45, 1)
bulk_df['volume']                = bulk_df['sets'] * bulk_df['reps']
bulk_df['intensity']             = bulk_df['weight'] / np.maximum(bulk_df['reps'], 1)
bulk_df['calories_per_kg']       = bulk_df['calories'] / np.maximum(bulk_df['weight'] * 0.45, 1)

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

def calculate_baseline_growth(row, time_months, current_size_cm, workout_time_years):
    M_max, k = get_baseline_params(row['age'], row['gender'], row['experience'], current_size_cm, workout_time_years)
    M0 = current_size_cm * 0.2
    baseline_growth = (M_max - M0) * (1 - np.exp(-k * time_months))
    return max(baseline_growth * 5, 0.1)

bulk_df['baseline_growth'] = bulk_df.apply(
    lambda r: calculate_baseline_growth(r, 3, 0, 0), axis=1)
bulk_df['adjustment_factor'] = np.clip(
    bulk_df['muscle_size_increase_cm2'] / bulk_df['baseline_growth'], 0.01, 10.0)

BULK_FEATURES = [
    'age','gender_encoded','exercise_name_encoded','sets','reps','weight',
    'frequency','protein','calories','sleep','experience_encoded',
    'muscle_group_encoded','category_encoded','protein_per_kg','volume',
    'intensity','calories_per_kg','genetic_advantage'
]
X_bulk = bulk_df[BULK_FEATURES].replace([np.inf,-np.inf], np.nan).fillna(bulk_df[BULK_FEATURES].median())
y_bulk = bulk_df['adjustment_factor']
X_tr, X_te, y_tr, y_te = train_test_split(X_bulk, y_bulk, test_size=0.3, random_state=42)
bulk_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
bulk_model.fit(X_tr, y_tr)
print(f"Bulk model ready. R²={bulk_model.score(X_te, y_te):.3f}")

def safe_enc(enc, val, default=0):
    return enc.transform([val])[0] if val in enc.classes_ else default

def predict_bulk(age, gender, exercises, frequency, protein, calories, sleep, experience,
                 current_size_cm=0, workout_time_years=0):
    difficulty = {'Compound':1.0,'Isolation':0.8}
    muscle_groups = {}
    for ex in exercises:
        mg = ex['target_muscle_group']
        muscle_groups.setdefault(mg, []).append(ex)

    results = {}
    for mg, ex_list in muscle_groups.items():
        total_vol, max_vol, primary = 0, 0, None
        for ex in ex_list:
            v = ex['sets'] * ex['reps'] * ex['weight'] * difficulty[ex['exercise_category']]
            total_vol += v
            if v > max_vol:
                max_vol, primary = v, ex

        predictions = {}
        for months in [3, 6, 9, 12]:
            baseline = calculate_baseline_growth(
                pd.Series({'age':age,'gender':gender,'experience':experience}),
                months, current_size_cm, workout_time_years)

            es = min(10, primary['sets'])
            er = min(20, primary['reps'])
            ew = min(300, total_vol / (es * er))

            inp = np.array([[
                age, safe_enc(le_b_gender, gender),
                safe_enc(le_b_exercise, primary['exercise_name']),
                es, er, ew, frequency, protein, calories, sleep,
                safe_enc(le_b_exp, experience),
                safe_enc(le_b_muscle, mg),
                safe_enc(le_b_category, primary['exercise_category']),
                protein / max(ew * 0.45, 1),
                es * er, ew / max(er, 1),
                calories / max(ew * 0.45, 1), 3
            ]])
            adj = np.clip(bulk_model.predict(inp)[0], 0.01, 10.0)
            adj *= min(1.3, 1 + 0.1 * (len(ex_list) - 1))
            predictions[months] = round(baseline * adj, 3)
        results[mg] = predictions
    return results

# ─────────────────────────────────────────────
#  CUT MODEL TRAINING
# ─────────────────────────────────────────────
print("Training Cut models…")
cut_df = pd.read_csv("fatLoss.csv")
np.random.seed(42)

# BMR
cut_df.loc[cut_df['gender']=='M','BMR'] = (88.362 + 13.397*cut_df.loc[cut_df['gender']=='M','current_weight']
    + 4.799*cut_df.loc[cut_df['gender']=='M','height'] - 5.677*cut_df.loc[cut_df['gender']=='M','age'])
cut_df.loc[cut_df['gender']=='F','BMR'] = (447.593 + 9.247*cut_df.loc[cut_df['gender']=='F','current_weight']
    + 3.098*cut_df.loc[cut_df['gender']=='F','height'] - 4.330*cut_df.loc[cut_df['gender']=='F','age'])

cut_df['BFP']                = np.random.uniform(5, 50, len(cut_df))
cut_df['BMI']                = cut_df['current_weight'] / ((cut_df['height']/100)**2)
cut_df['activity_level']     = cut_df['frequency'] * 5
cut_df['TDEE']               = cut_df['BMR'] * (1.2 + cut_df['activity_level']*0.1)
cut_df['estimated_fat_mass'] = (cut_df['BFP']/100) * cut_df['current_weight']
cut_df['muscle_mass']        = cut_df['current_weight'] - cut_df['estimated_fat_mass']
cut_df['training_intensity'] = (cut_df['weight']*cut_df['sets']*cut_df['reps']) / cut_df['current_weight']
cut_df['sleep_quality']      = np.where(cut_df['sleep']>=7.5, 1, cut_df['sleep']/7.5)
cut_df['protein_per_kg']     = cut_df['protein'] / cut_df['current_weight']
cut_df['deficit_ratio']      = cut_df['daily_deficit'] / cut_df['TDEE']
cut_df['volume']             = cut_df['sets'] * cut_df['reps'] * cut_df['weight']
cut_df['intensity']          = cut_df['weight'] / np.maximum(cut_df['reps'], 1)
cut_df['calories_per_kg']    = cut_df['calories'] / np.maximum(cut_df['current_weight'], 1)

le_c_gender    = LabelEncoder().fit(cut_df['gender'])
le_c_exp       = LabelEncoder().fit(cut_df['experience'])
le_c_type      = LabelEncoder().fit(cut_df['type'])
le_c_exercise  = LabelEncoder().fit(cut_df['exercise_name'])
le_c_muscle    = LabelEncoder().fit(cut_df['target_muscle_group'])
le_c_excat     = LabelEncoder().fit(cut_df['type'])  # same as type for cut data

cut_df['gender_encoded']           = le_c_gender.transform(cut_df['gender'])
cut_df['experience_encoded']       = le_c_exp.transform(cut_df['experience'])
cut_df['type_encoded']             = le_c_type.transform(cut_df['type'])
cut_df['exercise_name_encoded']    = le_c_exercise.transform(cut_df['exercise_name'])
cut_df['muscle_group_encoded']     = le_c_muscle.transform(cut_df['target_muscle_group'])
cut_df['exercise_category_encoded']= le_c_excat.transform(cut_df['type'])

cut_df['predicted_weight_after_loss'] = cut_df['current_weight'] - cut_df['actual_fat_loss']
cut_df['bfp_at_3']  = np.maximum(cut_df['BFP'] - np.random.uniform(2,5,len(cut_df)), np.where(cut_df['gender']=='M',3,8))
cut_df['bfp_at_6']  = np.maximum(cut_df['bfp_at_3'] - np.random.uniform(1,3,len(cut_df)), np.where(cut_df['gender']=='M',3,8))
cut_df['bfp_at_9']  = np.maximum(cut_df['bfp_at_6'] - np.random.uniform(0.5,2,len(cut_df)), np.where(cut_df['gender']=='M',3,8))
cut_df['bfp_at_12'] = np.maximum(cut_df['bfp_at_9'] - np.random.uniform(0.5,1.5,len(cut_df)), np.where(cut_df['gender']=='M',3,8))

mgf = 1 + (cut_df['training_intensity'] * 0.001)
for m in [3,6,9,12]:
    cut_df[f'muscle_mass_at_{m}'] = (cut_df['predicted_weight_after_loss']*(1-cut_df[f'bfp_at_{m}']/100))*mgf
    cut_df[f'definition_at_{m}']  = np.clip((cut_df[f'muscle_mass_at_{m}']/10)*(50-cut_df[f'bfp_at_{m}'])/10, 0, 5)

CUT_FEATURES = [
    'age','gender_encoded','current_weight','height','BMI',
    'sets','reps','weight','frequency','training_intensity',
    'protein','protein_per_kg','calories','sleep','sleep_quality',
    'experience_encoded','genetic_advantage','daily_deficit','deficit_ratio',
    'type_encoded','BFP','muscle_mass','TDEE','activity_level',
    'exercise_name_encoded','muscle_group_encoded','exercise_category_encoded',
    'volume','intensity','calories_per_kg'
]
X_cut = cut_df[CUT_FEATURES]
cut_models = {}
for interval in [3,6,9,12]:
    cut_models[interval] = {}
    for metric in ['bfp','muscle_mass','definition']:
        y = cut_df[f'{metric}_at_{interval}']
        Xtr,Xte,ytr,yte = train_test_split(X_cut,y,test_size=0.2,random_state=42)
        rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        rf.fit(Xtr, ytr)
        cut_models[interval][metric] = rf
print("Cut models ready.")

def predict_cut(age, gender, exercises, frequency, protein, calories, sleep, experience,
                genetic_advantage=3, daily_deficit=500, initial_bfp=20.0,
                current_weight=80.0, height=175.0):
    difficulty = {'Compound':1.0,'Isolation':0.8}
    total_vol, max_vol, primary = 0, 0, None
    for ex in exercises:
        v = ex['sets']*ex['reps']*ex['weight']*difficulty.get(ex.get('exercise_category','Compound'),1.0)
        total_vol += v
        if v > max_vol: max_vol, primary = v, ex

    es = min(10, primary['sets'])
    er = min(20, primary['reps'])
    ew = min(300, total_vol/(es*er))

    bmr = (88.362+13.397*current_weight+4.799*height-5.677*age) if gender=='M' \
          else (447.593+9.247*current_weight+3.098*height-4.330*age)
    bmi            = current_weight/((height/100)**2)
    activity_level = frequency*5
    tdee           = bmr*(1.2+activity_level*0.1)
    est_fat        = (initial_bfp/100)*current_weight
    muscle_mass    = current_weight - est_fat
    t_intensity    = (ew*es*er)/current_weight
    sleep_q        = 1 if sleep>=7.5 else sleep/7.5
    prot_per_kg    = protein/current_weight
    def_ratio      = daily_deficit/tdee
    vol            = es*er*ew
    intens         = ew/max(er,1)
    cal_per_kg     = calories/max(current_weight,1)

    inp = np.array([[
        age, safe_enc(le_c_gender,gender), current_weight, height, bmi,
        es, er, ew, frequency, t_intensity,
        protein, prot_per_kg, calories, sleep, sleep_q,
        safe_enc(le_c_exp,experience), genetic_advantage, daily_deficit, def_ratio,
        0, initial_bfp, muscle_mass, tdee, activity_level,
        safe_enc(le_c_exercise, primary['exercise_name']),
        safe_enc(le_c_muscle, primary.get('target_muscle_group','Chest')),
        safe_enc(le_c_excat, primary.get('exercise_category','Compound')),
        vol, intens, cal_per_kg
    ]])

    out = {}
    for interval in [3,6,9,12]:
        out[interval] = {
            m: max(cut_models[interval][m].predict(inp)[0], 0)
            for m in ['bfp','muscle_mass','definition']
        }
    return out

# ─────────────────────────────────────────────
#  CHART HELPERS
# ─────────────────────────────────────────────
MONTHS = [3, 6, 9, 12]
PALETTE = ['#6366f1','#f59e0b','#10b981','#ef4444','#8b5cf6','#06b6d4']

def make_bulk_chart(results: dict, title_suffix=""):
    if not results:
        return None
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor('#0f172a')
    for ax in axes:
        ax.set_facecolor('#1e293b')
        ax.tick_params(colors='#cbd5e1')
        ax.xaxis.label.set_color('#94a3b8')
        ax.yaxis.label.set_color('#94a3b8')
        ax.title.set_color('#f1f5f9')
        for spine in ax.spines.values():
            spine.set_edgecolor('#334155')

    # --- Left: line chart per muscle group ---
    for i, (mg, preds) in enumerate(results.items()):
        vals = [preds[m] for m in MONTHS]
        axes[0].plot(MONTHS, vals, marker='o', linewidth=2.5,
                     color=PALETTE[i % len(PALETTE)], label=mg, markersize=7)
        for x, y in zip(MONTHS, vals):
            axes[0].annotate(f"{y:.2f}", (x, y), textcoords="offset points",
                             xytext=(0, 9), ha='center', fontsize=8, color='#e2e8f0')
    axes[0].set_xticks(MONTHS)
    axes[0].set_xticklabels([f"{m}M" for m in MONTHS])
    axes[0].set_xlabel("Months")
    axes[0].set_ylabel("Predicted Growth (cm²)")
    axes[0].set_title("Muscle Growth Over Time")
    axes[0].legend(facecolor='#1e293b', labelcolor='#e2e8f0', framealpha=0.8)
    axes[0].grid(axis='y', color='#334155', linestyle='--', alpha=0.5)

    # --- Right: grouped bar at 12M ---
    mgs   = list(results.keys())
    vals12 = [results[mg][12] for mg in mgs]
    bars = axes[1].bar(mgs, vals12, color=PALETTE[:len(mgs)], width=0.5, zorder=3)
    for bar, v in zip(bars, vals12):
        axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05,
                     f"{v:.2f}", ha='center', va='bottom', color='#e2e8f0', fontsize=9)
    axes[1].set_ylabel("Growth (cm²)")
    axes[1].set_title("Projected Growth at 12 Months")
    axes[1].grid(axis='y', color='#334155', linestyle='--', alpha=0.5, zorder=0)
    axes[1].tick_params(axis='x', rotation=20)

    fig.suptitle(f"Bulk Predictor Results {title_suffix}", color='#f1f5f9',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    return fig

def make_cut_chart(results: dict):
    if not results:
        return None
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor('#0f172a')
    labels  = ['Body Fat %', 'Muscle Mass (kg)', 'Definition Score (0-5)']
    metrics = ['bfp', 'muscle_mass', 'definition']
    colors  = ['#ef4444', '#10b981', '#6366f1']

    for ax, metric, label, color in zip(axes, metrics, labels, colors):
        ax.set_facecolor('#1e293b')
        ax.tick_params(colors='#cbd5e1')
        ax.xaxis.label.set_color('#94a3b8')
        ax.yaxis.label.set_color('#94a3b8')
        ax.title.set_color('#f1f5f9')
        for spine in ax.spines.values():
            spine.set_edgecolor('#334155')

        vals = [results[m][metric] for m in MONTHS]
        ax.plot(MONTHS, vals, marker='o', linewidth=2.5, color=color, markersize=8)
        ax.fill_between(MONTHS, vals, alpha=0.15, color=color)
        for x, y in zip(MONTHS, vals):
            ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points",
                        xytext=(0, 10), ha='center', fontsize=9, color='#e2e8f0')
        ax.set_xticks(MONTHS)
        ax.set_xticklabels([f"{m}M" for m in MONTHS])
        ax.set_xlabel("Months")
        ax.set_ylabel(label)
        ax.set_title(label)
        ax.grid(axis='y', color='#334155', linestyle='--', alpha=0.5)

    fig.suptitle("Cut / Recomp Predictor Results", color='#f1f5f9',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    return fig

# ─────────────────────────────────────────────
#  STATE HELPERS — exercise table
# ─────────────────────────────────────────────
def build_table_html(exercises):
    if not exercises:
        return "<p style='color:#94a3b8;font-style:italic;padding:8px'>No exercises added yet.</p>"
    rows = ""
    for i, ex in enumerate(exercises):
        rows += f"""<tr>
          <td>{ex['exercise_name']}</td>
          <td>{ex['target_muscle_group']}</td>
          <td>{ex['exercise_category']}</td>
          <td>{ex['sets']}</td>
          <td>{ex['reps']}</td>
          <td>{ex['weight']} kg</td>
          <td><button onclick="gradioApp().querySelector('#remove_{i}').click()"
                style="background:#ef4444;color:white;border:none;border-radius:4px;
                       padding:2px 8px;cursor:pointer;font-size:12px">✕</button></td>
        </tr>"""
    return f"""
    <table style="width:100%;border-collapse:collapse;color:#e2e8f0;font-size:13px">
      <thead><tr style="background:#334155;text-align:left">
        <th style="padding:6px">Exercise</th><th>Muscle</th><th>Type</th>
        <th>Sets</th><th>Reps</th><th>Weight</th><th></th>
      </tr></thead>
      <tbody style="background:#1e293b">{rows}</tbody>
    </table>"""

# ─────────────────────────────────────────────
#  GRADIO UI
# ─────────────────────────────────────────────
CSS = """
body, .gradio-container { background:#0f172a !important; color:#e2e8f0 !important; }
.gr-panel, .gr-box, .gr-form { background:#1e293b !important; border:1px solid #334155 !important; border-radius:10px !important; }
label { color:#94a3b8 !important; font-size:13px !important; }
.gr-button-primary { background: linear-gradient(135deg,#6366f1,#8b5cf6) !important; border:none !important; color:white !important; font-weight:600 !important; }
.gr-button { background:#334155 !important; color:#e2e8f0 !important; border:1px solid #475569 !important; }
h1,h2,h3 { color:#f1f5f9 !important; }
.tab-nav button { color:#94a3b8 !important; background:transparent !important; border-bottom:2px solid transparent !important; }
.tab-nav button.selected { color:#6366f1 !important; border-bottom:2px solid #6366f1 !important; }
"""

DESCRIPTION = """
<div style="text-align:center;padding:16px 0 8px">
  <h1 style="font-size:2rem;font-weight:800;background:linear-gradient(135deg,#6366f1,#10b981);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0">
    FitPredictor AI
  </h1>
  <p style="color:#94a3b8;margin-top:6px">
    ML-powered body composition forecasting · Bulk or Cut · 3–12 month timeline
  </p>
</div>
"""

def run_bulk(age, gender, frequency, protein, calories, sleep, experience,
             current_size, workout_years, ex_state):
    if not ex_state:
        return None, "⚠️ Please add at least one exercise."
    try:
        results = predict_bulk(int(age), gender, ex_state, int(frequency),
                               float(protein), int(calories), float(sleep),
                               experience, float(current_size), float(workout_years))
        fig = make_bulk_chart(results)
        summary = "\n".join(
            f"**{mg}** — 3M: {p[3]:.2f} | 6M: {p[6]:.2f} | 9M: {p[9]:.2f} | 12M: {p[12]:.2f} cm²"
            for mg, p in results.items()
        )
        return fig, summary
    except Exception as e:
        return None, f"❌ Error: {e}"

def run_cut(age, gender, frequency, protein, calories, sleep, experience,
            weight, height, bfp, deficit, genetic_adv, ex_state):
    if not ex_state:
        return None, "⚠️ Please add at least one exercise."
    try:
        results = predict_cut(int(age), gender, ex_state, int(frequency),
                              float(protein), int(calories), float(sleep),
                              experience, int(genetic_adv), float(deficit),
                              float(bfp), float(weight), float(height))
        fig = make_cut_chart(results)
        summary = "\n".join(
            f"**Month {m}** — BF%: {r['bfp']:.1f}% | Muscle: {r['muscle_mass']:.1f}kg | Definition: {r['definition']:.2f}/5"
            for m, r in results.items()
        )
        return fig, summary
    except Exception as e:
        return None, f"❌ Error: {e}"

def add_exercise(name, state):
    if state is None: state = []
    ex = {
        'exercise_name': name,
        'target_muscle_group': get_muscle(name),
        'exercise_category': get_type(name),
        'sets': 3, 'reps': 10, 'weight': 60
    }
    state = state + [ex]
    return state, build_table_html(state)

def update_exercise(state, idx, field, value):
    if state and 0 <= idx < len(state):
        state = [dict(e) for e in state]
        state[idx][field] = value
    return state, build_table_html(state)

def remove_exercise(state, idx):
    if state and 0 <= idx < len(state):
        state = [e for i,e in enumerate(state) if i != idx]
    return state, build_table_html(state)

def clear_exercises(state):
    return [], "<p style='color:#94a3b8;font-style:italic;padding:8px'>No exercises added yet.</p>"

with gr.Blocks(css=CSS, title="FitPredictor AI") as demo:
    gr.HTML(DESCRIPTION)

    with gr.Tabs():
        # ── BULK TAB ────────────────────────────────────────────────
        with gr.Tab("💪 Bulk — Muscle Growth"):
            bulk_ex_state = gr.State([])

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Personal Info")
                    b_age    = gr.Slider(18, 65, value=25, step=1, label="Age")
                    b_gender = gr.Radio(GENDERS, value='M', label="Gender")
                    b_exp    = gr.Dropdown(EXPERIENCE, value='Intermediate', label="Experience")
                    b_freq   = gr.Slider(1, 7, value=4, step=1, label="Workout days / week")
                    b_csz    = gr.Slider(0, 50, value=0, step=1, label="Current muscle size (cm)")
                    b_yrs    = gr.Slider(0, 10, value=0, step=0.5, label="Years training")
                    gr.Markdown("### Nutrition & Recovery")
                    b_prot   = gr.Slider(50, 300, value=150, step=5, label="Daily Protein (g)")
                    b_cal    = gr.Slider(1500, 5000, value=2800, step=50, label="Daily Calories (kcal)")
                    b_sleep  = gr.Slider(4, 12, value=7.5, step=0.5, label="Sleep (hours)")

                with gr.Column(scale=2):
                    gr.Markdown("### Exercise Plan")
                    with gr.Row():
                        b_ex_name = gr.Dropdown(EXERCISES, value=EXERCISES[0], label="Exercise", scale=3)
                        b_add_btn = gr.Button("➕ Add Exercise", variant="primary", scale=1)

                    b_table_html = gr.HTML(build_table_html([]))

                    with gr.Accordion("✏️ Edit exercise details", open=False):
                        with gr.Row():
                            b_edit_idx  = gr.Number(value=0, label="Row # (0-indexed)", precision=0)
                            b_edit_sets = gr.Slider(1,10,value=3,step=1,label="Sets")
                            b_edit_reps = gr.Slider(1,20,value=10,step=1,label="Reps")
                            b_edit_wt   = gr.Slider(1,300,value=60,step=2.5,label="Weight (kg)")
                        b_edit_btn  = gr.Button("Update row")
                        b_clear_btn = gr.Button("🗑 Clear all exercises")

                    b_predict_btn = gr.Button("🚀 Predict Muscle Growth", variant="primary", size="lg")

            b_plot    = gr.Plot(label="Growth Timeline")
            b_summary = gr.Markdown()

            b_add_btn.click(add_exercise, [b_ex_name, bulk_ex_state], [bulk_ex_state, b_table_html])
            b_edit_btn.click(
                lambda s,i,sets,reps,wt: update_exercise(s,int(i),'sets',int(sets)) and None or
                    update_exercise(update_exercise(s,int(i),'sets',int(sets))[0],int(i),'reps',int(reps)) and None or
                    update_exercise(update_exercise(update_exercise(s,int(i),'sets',int(sets))[0],int(i),'reps',int(reps))[0],int(i),'weight',float(wt)),
                [bulk_ex_state, b_edit_idx, b_edit_sets, b_edit_reps, b_edit_wt],
                [bulk_ex_state, b_table_html]
            )

            def bulk_edit_all(s,i,sets,reps,wt):
                s = [dict(e) for e in (s or [])]
                idx = int(i)
                if 0 <= idx < len(s):
                    s[idx]['sets']   = int(sets)
                    s[idx]['reps']   = int(reps)
                    s[idx]['weight'] = float(wt)
                return s, build_table_html(s)

            b_edit_btn.click(bulk_edit_all,
                [bulk_ex_state, b_edit_idx, b_edit_sets, b_edit_reps, b_edit_wt],
                [bulk_ex_state, b_table_html])
            b_clear_btn.click(clear_exercises, [bulk_ex_state], [bulk_ex_state, b_table_html])
            b_predict_btn.click(
                run_bulk,
                [b_age,b_gender,b_freq,b_prot,b_cal,b_sleep,b_exp,b_csz,b_yrs,bulk_ex_state],
                [b_plot, b_summary]
            )

        # ── CUT TAB ────────────────────────────────────────────────
        with gr.Tab("🔥 Cut — Body Recomposition"):
            cut_ex_state = gr.State([])

            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Personal Info")
                    c_age    = gr.Slider(18, 65, value=28, step=1, label="Age")
                    c_gender = gr.Radio(GENDERS, value='M', label="Gender")
                    c_exp    = gr.Dropdown(EXPERIENCE, value='Intermediate', label="Experience")
                    c_weight = gr.Slider(40, 150, value=85, step=0.5, label="Current Weight (kg)")
                    c_height = gr.Slider(140, 220, value=175, step=1, label="Height (cm)")
                    c_bfp    = gr.Slider(5, 50, value=20, step=0.5, label="Current Body Fat %")
                    c_freq   = gr.Slider(1, 7, value=4, step=1, label="Workout days / week")
                    gr.Markdown("### Nutrition & Recovery")
                    c_prot   = gr.Slider(50, 300, value=150, step=5, label="Daily Protein (g)")
                    c_cal    = gr.Slider(1200, 5000, value=2200, step=50, label="Daily Calories (kcal)")
                    c_sleep  = gr.Slider(4, 12, value=8, step=0.5, label="Sleep (hours)")
                    c_def    = gr.Slider(100, 1000, value=500, step=50, label="Daily Caloric Deficit (kcal)")
                    c_gen    = gr.Slider(1, 5, value=3, step=1, label="Genetic Advantage (1–5)")

                with gr.Column(scale=2):
                    gr.Markdown("### Exercise Plan")
                    with gr.Row():
                        c_ex_name = gr.Dropdown(EXERCISES, value=EXERCISES[0], label="Exercise", scale=3)
                        c_add_btn = gr.Button("➕ Add Exercise", variant="primary", scale=1)

                    c_table_html = gr.HTML(build_table_html([]))

                    with gr.Accordion("✏️ Edit exercise details", open=False):
                        with gr.Row():
                            c_edit_idx  = gr.Number(value=0, label="Row # (0-indexed)", precision=0)
                            c_edit_sets = gr.Slider(1,10,value=3,step=1,label="Sets")
                            c_edit_reps = gr.Slider(1,20,value=10,step=1,label="Reps")
                            c_edit_wt   = gr.Slider(1,300,value=60,step=2.5,label="Weight (kg)")
                        c_edit_btn  = gr.Button("Update row")
                        c_clear_btn = gr.Button("🗑 Clear all exercises")

                    c_predict_btn = gr.Button("🚀 Predict Body Recomposition", variant="primary", size="lg")

            c_plot    = gr.Plot(label="Body Composition Timeline")
            c_summary = gr.Markdown()

            def cut_edit_all(s,i,sets,reps,wt):
                s = [dict(e) for e in (s or [])]
                idx = int(i)
                if 0 <= idx < len(s):
                    s[idx]['sets']   = int(sets)
                    s[idx]['reps']   = int(reps)
                    s[idx]['weight'] = float(wt)
                return s, build_table_html(s)

            c_add_btn.click(add_exercise, [c_ex_name, cut_ex_state], [cut_ex_state, c_table_html])
            c_edit_btn.click(cut_edit_all,
                [cut_ex_state, c_edit_idx, c_edit_sets, c_edit_reps, c_edit_wt],
                [cut_ex_state, c_table_html])
            c_clear_btn.click(clear_exercises, [cut_ex_state], [cut_ex_state, c_table_html])
            c_predict_btn.click(
                run_cut,
                [c_age,c_gender,c_freq,c_prot,c_cal,c_sleep,c_exp,
                 c_weight,c_height,c_bfp,c_def,c_gen,cut_ex_state],
                [c_plot, c_summary]
            )

if __name__ == "__main__":
    demo.launch()
