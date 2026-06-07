"use client";
import { useState } from "react";
import Link from "next/link";
import ExerciseBuilder, { type Exercise } from "../components/ExerciseBuilder";
import { Field, Grid } from "../components/Field";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

interface BulkResult {
  [month: string]: { [muscleGrowth: string]: string };
}

export default function BulkPage() {
  const [exercises, setExercises] = useState<Exercise[]>([
    {
      exercise_name: "Barbell Bench Press",
      sets: 3,
      reps: 10,
      weight: 80,
      target_muscle_group: "Chest",
      exercise_category: "Compound",
    },
  ]);

  const [form, setForm] = useState({
    age: 24,
    gender: "M",
    frequency: 4,
    protein: 150,
    calories: 2800,
    sleep: 7.5,
    experience: "Intermediate",
    current_size_cm: 30,
    workout_time_years: 1,
  });

  const [result, setResult] = useState<BulkResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const set = (k: string, v: string | number) => setForm((f) => ({ ...f, [k]: v }));

  const predict = async () => {
    if (exercises.length === 0) {
      setError("Add at least one exercise.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API}/bulk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, exercises }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Prediction failed");
      setResult(data.result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  const months = [3, 6, 9, 12];

  return (
    <main style={{ minHeight: "100vh", padding: "40px 20px", maxWidth: 800, margin: "0 auto" }}>
      {/* Nav */}
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 40 }}>
        <Link
          href="/"
          style={{
            color: "var(--muted)",
            textDecoration: "none",
            fontSize: 13,
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          ← Back
        </Link>
        <div className="pill">BULK</div>
        <h1
          style={{
            fontFamily: "Syne, sans-serif",
            fontSize: 22,
            fontWeight: 700,
            marginLeft: "auto",
          }}
        >
          Muscle Growth Predictor
        </h1>
      </div>

      {/* Form */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h2
          style={{
            fontFamily: "Syne, sans-serif",
            fontSize: 14,
            fontWeight: 600,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            color: "var(--muted)",
            marginBottom: 20,
          }}
        >
          Personal Info
        </h2>
        <Grid cols={3}>
          <Field label="Age">
            <input
              type="number"
              value={form.age}
              onChange={(e) => set("age", +e.target.value)}
              min={18}
              max={80}
            />
          </Field>
          <Field label="Gender">
            <select value={form.gender} onChange={(e) => set("gender", e.target.value)}>
              <option value="M">Male</option>
              <option value="F">Female</option>
            </select>
          </Field>
          <Field label="Experience">
            <select value={form.experience} onChange={(e) => set("experience", e.target.value)}>
              <option>Beginner</option>
              <option>Intermediate</option>
              <option>Advanced</option>
            </select>
          </Field>
        </Grid>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2
          style={{
            fontFamily: "Syne, sans-serif",
            fontSize: 14,
            fontWeight: 600,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            color: "var(--muted)",
            marginBottom: 20,
          }}
        >
          Lifestyle & Nutrition
        </h2>
        <Grid cols={2}>
          <Field label="Training Frequency (days/wk)">
            <input
              type="number"
              value={form.frequency}
              onChange={(e) => set("frequency", +e.target.value)}
              min={1}
              max={7}
            />
          </Field>
          <Field label="Daily Protein (g)">
            <input
              type="number"
              value={form.protein}
              onChange={(e) => set("protein", +e.target.value)}
            />
          </Field>
          <Field label="Daily Calories (kcal)">
            <input
              type="number"
              value={form.calories}
              onChange={(e) => set("calories", +e.target.value)}
            />
          </Field>
          <Field label="Sleep (hours)">
            <input
              type="number"
              step="0.5"
              value={form.sleep}
              onChange={(e) => set("sleep", +e.target.value)}
            />
          </Field>
          <Field label="Current Muscle Size (cm)">
            <input
              type="number"
              value={form.current_size_cm}
              onChange={(e) => set("current_size_cm", +e.target.value)}
            />
          </Field>
          <Field label="Training History (years)">
            <input
              type="number"
              step="0.5"
              value={form.workout_time_years}
              onChange={(e) => set("workout_time_years", +e.target.value)}
            />
          </Field>
        </Grid>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2
          style={{
            fontFamily: "Syne, sans-serif",
            fontSize: 14,
            fontWeight: 600,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            color: "var(--muted)",
            marginBottom: 20,
          }}
        >
          Exercises
        </h2>
        <ExerciseBuilder exercises={exercises} onChange={setExercises} />
      </div>

      {error && (
        <div
          style={{
            background: "rgba(255,60,60,0.1)",
            border: "1px solid rgba(255,60,60,0.3)",
            borderRadius: 8,
            padding: "12px 16px",
            color: "#ff6060",
            fontSize: 13,
            marginBottom: 16,
          }}
        >
          {error}
        </div>
      )}

      <button
        className="btn-primary"
        onClick={predict}
        disabled={loading}
        style={{ width: "100%", padding: "14px 0", fontSize: 15 }}
      >
        {loading ? (
          <span>
            Predicting
            <span className="loading-dot" style={{ marginLeft: 4 }}>.</span>
            <span className="loading-dot">.</span>
            <span className="loading-dot">.</span>
          </span>
        ) : (
          "Predict Muscle Growth →"
        )}
      </button>

      {/* Results */}
      {result && (
        <div className="fade-up" style={{ marginTop: 32 }}>
          <h2
            style={{
              fontFamily: "Syne, sans-serif",
              fontSize: 20,
              fontWeight: 700,
              marginBottom: 20,
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            Results
            <span className="pill">Growth (cm²)</span>
          </h2>

          {/* Month tabs */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: 12,
              marginBottom: 24,
            }}
          >
            {months.map((m) => (
              <div
                key={m}
                className="card"
                style={{ textAlign: "center", padding: "16px 12px" }}
              >
                <div
                  style={{
                    color: "var(--accent)",
                    fontFamily: "Syne, sans-serif",
                    fontWeight: 800,
                    fontSize: 24,
                    marginBottom: 4,
                  }}
                >
                  {m}
                </div>
                <div style={{ color: "var(--muted)", fontSize: 11, letterSpacing: "0.06em" }}>
                  MONTHS
                </div>
              </div>
            ))}
          </div>

          {/* Muscle breakdown per month */}
          {months.map((m) => {
            const monthData = result[String(m)];
            if (!monthData) return null;
            return (
              <div key={m} className="card" style={{ marginBottom: 12 }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 10,
                    marginBottom: 14,
                  }}
                >
                  <span
                    style={{
                      fontFamily: "Syne, sans-serif",
                      fontWeight: 700,
                      fontSize: 16,
                    }}
                  >
                    Month {m}
                  </span>
                </div>
                {Object.entries(monthData).map(([key, val]) => {
                  const muscle = key.replace(" growth", "");
                  const num = parseFloat(val);
                  const pct = Math.min(100, (num / 5) * 100);
                  return (
                    <div key={key} style={{ marginBottom: 12 }}>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          marginBottom: 6,
                        }}
                      >
                        <span style={{ fontSize: 13 }}>{muscle}</span>
                        <span
                          style={{
                            color: "var(--accent)",
                            fontFamily: "DM Mono, monospace",
                            fontSize: 13,
                            fontWeight: 500,
                          }}
                        >
                          {val}
                        </span>
                      </div>
                      <div
                        style={{
                          height: 4,
                          background: "var(--border)",
                          borderRadius: 2,
                          overflow: "hidden",
                        }}
                      >
                        <div
                          style={{
                            height: "100%",
                            width: `${pct}%`,
                            background: "var(--accent)",
                            borderRadius: 2,
                            transition: "width 0.6s ease",
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      )}
    </main>
  );
}
