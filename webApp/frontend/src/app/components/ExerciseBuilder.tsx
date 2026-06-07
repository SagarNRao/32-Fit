"use client";
import { useState } from "react";

export interface Exercise {
  exercise_name: string;
  sets: number;
  reps: number;
  weight: number;
  target_muscle_group: string;
  exercise_category: "Compound" | "Isolation";
}

const MUSCLE_GROUPS = [
  "Biceps", "Triceps", "Chest", "Back", "Shoulders",
  "Legs", "Abs", "Glutes", "Calves", "Forearms",
];

const EXERCISES: Record<string, string[]> = {
  Chest:     ["Barbell Bench Press", "Dumbbell Fly", "Incline Press", "Cable Crossover"],
  Back:      ["Barbell Rows", "Lat Pulldowns", "Pull-ups", "Seated Cable Rows"],
  Legs:      ["Squats", "Deadlifts", "Leg Press", "Leg Curls"],
  Biceps:    ["Dumbbell Curls", "Barbell Curls", "Hammer Curls", "Preacher Curls"],
  Triceps:   ["Tricep Extensions", "Skull Crushers", "Cable Pushdowns", "Dips"],
  Shoulders: ["Dumbbell Press", "Lateral Raises", "Front Raises", "Arnold Press"],
  Abs:       ["Crunches", "Planks", "Leg Raises", "Cable Crunches"],
  Glutes:    ["Hip Thrusts", "Romanian Deadlifts", "Glute Bridges", "Kickbacks"],
  Calves:    ["Standing Calf Raises", "Seated Calf Raises"],
  Forearms:  ["Wrist Curls", "Reverse Curls"],
};

const COMPOUND_EXERCISES = new Set([
  "Barbell Bench Press", "Barbell Rows", "Squats", "Deadlifts",
  "Pull-ups", "Lat Pulldowns", "Incline Press", "Dips",
  "Romanian Deadlifts", "Hip Thrusts", "Arnold Press",
]);

interface Props {
  exercises: Exercise[];
  onChange: (exercises: Exercise[]) => void;
}

export default function ExerciseBuilder({ exercises, onChange }: Props) {
  const [muscle, setMuscle] = useState("Chest");

  const addExercise = () => {
    const name = EXERCISES[muscle]?.[0] || "Barbell Bench Press";
    onChange([
      ...exercises,
      {
        exercise_name: name,
        sets: 3,
        reps: 10,
        weight: 60,
        target_muscle_group: muscle,
        exercise_category: COMPOUND_EXERCISES.has(name) ? "Compound" : "Isolation",
      },
    ]);
  };

  const updateExercise = (i: number, field: keyof Exercise, value: string | number) => {
    const updated = exercises.map((ex, idx) => {
      if (idx !== i) return ex;
      const next = { ...ex, [field]: value } as Exercise;
      if (field === "exercise_name") {
        next.exercise_category = COMPOUND_EXERCISES.has(value as string) ? "Compound" : "Isolation";
      }
      return next;
    });
    onChange(updated);
  };

  const remove = (i: number) => onChange(exercises.filter((_, idx) => idx !== i));

  return (
    <div>
      {exercises.map((ex, i) => (
        <div
          key={i}
          className="card"
          style={{ marginBottom: 12, padding: 16, position: "relative" }}
        >
          <button
            onClick={() => remove(i)}
            style={{
              position: "absolute",
              top: 12,
              right: 12,
              background: "none",
              border: "none",
              color: "var(--muted)",
              cursor: "pointer",
              fontSize: 16,
              lineHeight: 1,
            }}
          >
            ×
          </button>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 12,
              marginBottom: 12,
            }}
          >
            <div>
              <div className="label">Muscle Group</div>
              <select
                value={ex.target_muscle_group}
                onChange={(e) => {
                  updateExercise(i, "target_muscle_group", e.target.value);
                  const first = EXERCISES[e.target.value]?.[0] || "";
                  updateExercise(i, "exercise_name", first);
                }}
              >
                {MUSCLE_GROUPS.map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </div>
            <div>
              <div className="label">Exercise</div>
              <select
                value={ex.exercise_name}
                onChange={(e) => updateExercise(i, "exercise_name", e.target.value)}
              >
                {(EXERCISES[ex.target_muscle_group] || []).map((name) => (
                  <option key={name}>{name}</option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            {(["sets", "reps", "weight"] as const).map((field) => (
              <div key={field}>
                <div className="label">
                  {field === "weight" ? "Weight (kg)" : field}
                </div>
                <input
                  type="number"
                  value={ex[field]}
                  min={field === "weight" ? 1 : 1}
                  max={field === "sets" ? 10 : field === "reps" ? 20 : 300}
                  onChange={(e) => updateExercise(i, field, Number(e.target.value))}
                />
              </div>
            ))}
          </div>

          <div style={{ marginTop: 10 }}>
            <span
              className="pill"
              style={{
                background: ex.exercise_category === "Compound"
                  ? "rgba(200,255,0,0.08)"
                  : "rgba(255,150,0,0.08)",
                color: ex.exercise_category === "Compound" ? "var(--accent)" : "#ff9600",
                borderColor: ex.exercise_category === "Compound"
                  ? "rgba(200,255,0,0.2)"
                  : "rgba(255,150,0,0.2)",
              }}
            >
              {ex.exercise_category}
            </span>
          </div>
        </div>
      ))}

      <div style={{ display: "flex", gap: 10, alignItems: "center", marginTop: 4 }}>
        <select
          value={muscle}
          onChange={(e) => setMuscle(e.target.value)}
          style={{ flex: 1 }}
        >
          {MUSCLE_GROUPS.map((m) => (
            <option key={m}>{m}</option>
          ))}
        </select>
        <button className="btn-ghost" onClick={addExercise}>
          + Add Exercise
        </button>
      </div>
    </div>
  );
}
