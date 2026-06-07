"use client";
import { useState } from "react";
import Link from "next/link";
import ExerciseBuilder, { type Exercise } from "../components/ExerciseBuilder";
import { Field, Grid } from "../components/Field";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001";

interface CutMonthResult {
  bfp: number;
  muscle_mass: number;
  definition: number;
}

interface CutResult {
  [month: string]: CutMonthResult;
}

const MONTHS = [3, 6, 9, 12];

function DefinitionBar({ score }: { score: number }) {
  const filled = Math.round(score);
  return (
    <div style={{ display: "flex", gap: 4 }}>
      {[1, 2, 3, 4, 5].map((n) => (
        <div
          key={n}
          style={{
            width: 20,
            height: 6,
            borderRadius: 3,
            background:
              n <= filled
                ? "linear-gradient(90deg, #00cfff, var(--accent))"
                : "var(--border)",
            transition: "background 0.3s",
          }}
        />
      ))}
    </div>
  );
}

export default function CutPage() {
  const [exercises, setExercises] = useState<Exercise[]>([
    {
      exercise_name: "Squats",
      sets: 4,
      reps: 10,
      weight: 80,
      target_muscle_group: "Legs",
      exercise_category: "Compound",
    },
  ]);

  const [form, setForm] = useState({
    age: 26,
    gender: "M",
    frequency: 4,
    protein: 160,
    calories: 2200,
    sleep: 8,
    experience: "Intermediate",
    genetic_advantage: 3,
    daily_deficit: 500,
    initial_bfp: 20,
    current_weight: 82,
    height: 178,
  });

  const [result, setResult] = useState<CutResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeMonth, setActiveMonth] = useState(3);

  const set = (k: string, v: string | number) => setForm((f) => ({ ...f, [k]: v }));

  const predict = async () => {
    if (exercises.length === 0) {
      setError("Add at least one exercise.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API}/cut`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, exercises }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Prediction failed");
      setResult(data.result);
      setActiveMonth(3);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  const active = result ? result[String(activeMonth)] : null;

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
        <div
          className="pill"
          style={{
            background: "rgba(0,207,255,0.1)",
            color: "#00cfff",
            borderColor: "rgba(0,207,255,0.2)",
          }}
        >
          CUT
        </div>
        <h1
          style={{
            fontFamily: "Syne, sans-serif",
            fontSize: 22,
            fontWeight: 700,
            marginLeft: "auto",
          }}
        >
          Body Composition Predictor
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
          Body Stats
        </h2>
        <Grid cols={3}>
          <Field label="Age">
            <input type="number" value={form.age} onChange={(e) => set("age", +e.target.value)} min={18} max={80} />
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
          <Field label="Weight (kg)">
            <input type="number" value={form.current_weight} onChange={(e) => set("current_weight", +e.target.value)} />
          </Field>
          <Field label="Height (cm)">
            <input type="number" value={form.height} onChange={(e) => set("height", +e.target.value)} />
          </Field>
          <Field label="Body Fat % (initial)">
            <input type="number" step="0.5" value={form.initial_bfp} onChange={(e) => set("initial_bfp", +e.target.value)} />
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
          Nutrition & Training
        </h2>
        <Grid cols={2}>
          <Field label="Frequency (days/wk)">
            <input type="number" value={form.frequency} onChange={(e) => set("frequency", +e.target.value)} min={1} max={7} />
          </Field>
          <Field label="Daily Deficit (kcal)">
            <input type="number" value={form.daily_deficit} onChange={(e) => set("daily_deficit", +e.target.value)} />
          </Field>
          <Field label="Daily Calories (kcal)">
            <input type="number" value={form.calories} onChange={(e) => set("calories", +e.target.value)} />
          </Field>
          <Field label="Daily Protein (g)">
            <input type="number" value={form.protein} onChange={(e) => set("protein", +e.target.value)} />
          </Field>
          <Field label="Sleep (hours)">
            <input type="number" step="0.5" value={form.sleep} onChange={(e) => set("sleep", +e.target.value)} />
          </Field>
          <Field label="Genetic Advantage (1–5)">
            <input type="number" min={1} max={5} value={form.genetic_advantage} onChange={(e) => set("genetic_advantage", +e.target.value)} />
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
        style={{
          width: "100%",
          padding: "14px 0",
          fontSize: 15,
          background: loading ? "var(--accent)" : "var(--accent)",
        }}
      >
        {loading ? (
          <span>
            Predicting
            <span className="loading-dot" style={{ marginLeft: 4 }}>.</span>
            <span className="loading-dot">.</span>
            <span className="loading-dot">.</span>
          </span>
        ) : (
          "Predict Body Composition →"
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
            }}
          >
            Your Journey
          </h2>

          {/* Month selector */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: 8,
              marginBottom: 24,
            }}
          >
            {MONTHS.map((m) => (
              <button
                key={m}
                onClick={() => setActiveMonth(m)}
                style={{
                  padding: "12px 8px",
                  borderRadius: 8,
                  border: `1px solid ${activeMonth === m ? "#00cfff" : "var(--border)"}`,
                  background: activeMonth === m ? "rgba(0,207,255,0.08)" : "var(--surface)",
                  color: activeMonth === m ? "#00cfff" : "var(--muted)",
                  fontFamily: "Syne, sans-serif",
                  fontWeight: 700,
                  fontSize: 14,
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                Mo. {m}
              </button>
            ))}
          </div>

          {/* Active month card */}
          {active && (
            <div
              className="card"
              style={{
                borderColor: "rgba(0,207,255,0.25)",
                padding: 28,
              }}
            >
              <div
                style={{
                  fontSize: 13,
                  color: "#00cfff",
                  fontFamily: "Syne, sans-serif",
                  fontWeight: 600,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  marginBottom: 24,
                }}
              >
                Month {activeMonth} Projection
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                  gap: 20,
                }}
              >
                {/* BFP */}
                <div>
                  <div className="label">Body Fat %</div>
                  <div
                    style={{
                      fontFamily: "Syne, sans-serif",
                      fontWeight: 800,
                      fontSize: 36,
                      color: "#00cfff",
                      lineHeight: 1.1,
                    }}
                  >
                    {active.bfp.toFixed(1)}
                    <span style={{ fontSize: 16, fontWeight: 400, color: "var(--muted)", marginLeft: 2 }}>%</span>
                  </div>
                  <div style={{ marginTop: 8, color: "var(--muted)", fontSize: 12 }}>
                    from {form.initial_bfp}% (−{(form.initial_bfp - active.bfp).toFixed(1)}%)
                  </div>
                </div>

                {/* Muscle Mass */}
                <div>
                  <div className="label">Lean Muscle Mass</div>
                  <div
                    style={{
                      fontFamily: "Syne, sans-serif",
                      fontWeight: 800,
                      fontSize: 36,
                      color: "var(--accent)",
                      lineHeight: 1.1,
                    }}
                  >
                    {active.muscle_mass.toFixed(1)}
                    <span style={{ fontSize: 16, fontWeight: 400, color: "var(--muted)", marginLeft: 2 }}>kg</span>
                  </div>
                </div>

                {/* Definition */}
                <div>
                  <div className="label">Definition Score</div>
                  <div
                    style={{
                      fontFamily: "Syne, sans-serif",
                      fontWeight: 800,
                      fontSize: 36,
                      color: "var(--text)",
                      lineHeight: 1.1,
                      marginBottom: 8,
                    }}
                  >
                    {active.definition.toFixed(1)}
                    <span style={{ fontSize: 16, fontWeight: 400, color: "var(--muted)", marginLeft: 2 }}>/5</span>
                  </div>
                  <DefinitionBar score={active.definition} />
                </div>
              </div>
            </div>
          )}

          {/* Timeline table */}
          <div className="card" style={{ marginTop: 16, padding: "20px 24px" }}>
            <div className="label" style={{ marginBottom: 14 }}>Full Timeline</div>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["Month", "Body Fat %", "Muscle Mass (kg)", "Definition"].map((h) => (
                    <th
                      key={h}
                      style={{
                        textAlign: "left",
                        color: "var(--muted)",
                        fontWeight: 400,
                        fontSize: 11,
                        letterSpacing: "0.06em",
                        textTransform: "uppercase",
                        paddingBottom: 10,
                        paddingRight: 16,
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {MONTHS.map((m) => {
                  const row = result[String(m)];
                  if (!row) return null;
                  return (
                    <tr
                      key={m}
                      style={{
                        borderBottom: "1px solid var(--border)",
                        background: m === activeMonth ? "var(--accent-dim)" : "transparent",
                        cursor: "pointer",
                      }}
                      onClick={() => setActiveMonth(m)}
                    >
                      <td style={{ padding: "12px 16px 12px 0", fontFamily: "Syne, sans-serif", fontWeight: 700 }}>
                        {m}
                      </td>
                      <td style={{ padding: "12px 16px 12px 0", color: "#00cfff" }}>
                        {row.bfp.toFixed(1)}%
                      </td>
                      <td style={{ padding: "12px 16px 12px 0", color: "var(--accent)" }}>
                        {row.muscle_mass.toFixed(1)} kg
                      </td>
                      <td style={{ padding: "12px 0" }}>
                        <DefinitionBar score={row.definition} />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </main>
  );
}
