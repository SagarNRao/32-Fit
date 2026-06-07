"use client";
import Link from "next/link";

export default function Home() {
  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 20px",
        background: "var(--bg)",
      }}
    >
      {/* Logo mark */}
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: 12,
          background: "var(--accent)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: 32,
          fontFamily: "Syne, sans-serif",
          fontWeight: 800,
          fontSize: 22,
          color: "#000",
        }}
      >
        F
      </div>

      <h1
        style={{
          fontFamily: "Syne, sans-serif",
          fontSize: "clamp(36px, 6vw, 64px)",
          fontWeight: 800,
          letterSpacing: "-0.03em",
          textAlign: "center",
          lineHeight: 1.1,
          marginBottom: 16,
        }}
      >
        FitPredictor
      </h1>

      <p
        style={{
          color: "var(--muted)",
          fontSize: 15,
          textAlign: "center",
          maxWidth: 400,
          lineHeight: 1.6,
          marginBottom: 52,
        }}
      >
        ML-powered predictions for your training goals. Choose your path.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: 20,
          width: "100%",
          maxWidth: 640,
        }}
      >
        {/* BULK card */}
        <Link href="/bulk" style={{ textDecoration: "none" }}>
          <div
            className="card"
            style={{
              cursor: "pointer",
              transition: "border-color 0.2s, transform 0.15s",
              position: "relative",
              overflow: "hidden",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = "var(--accent)";
              (e.currentTarget as HTMLElement).style.transform = "translateY(-3px)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = "var(--border)";
              (e.currentTarget as HTMLElement).style.transform = "translateY(0)";
            }}
          >
            <div
              style={{
                position: "absolute",
                top: -30,
                right: -30,
                width: 100,
                height: 100,
                borderRadius: "50%",
                background: "var(--accent-dim)",
                filter: "blur(20px)",
              }}
            />
            <div style={{ fontSize: 28, marginBottom: 14 }}>💪</div>
            <div className="pill" style={{ marginBottom: 10 }}>
              Muscle Growth
            </div>
            <h2
              style={{
                fontFamily: "Syne, sans-serif",
                fontSize: 22,
                fontWeight: 700,
                marginBottom: 8,
              }}
            >
              BULK
            </h2>
            <p style={{ color: "var(--muted)", fontSize: 13, lineHeight: 1.6 }}>
              Predict per-muscle hypertrophy (cm²) at 3, 6, 9 & 12 months based on your exercises,
              nutrition, and training history.
            </p>
          </div>
        </Link>

        {/* CUT card */}
        <Link href="/cut" style={{ textDecoration: "none" }}>
          <div
            className="card"
            style={{
              cursor: "pointer",
              transition: "border-color 0.2s, transform 0.15s",
              position: "relative",
              overflow: "hidden",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = "#00cfff";
              (e.currentTarget as HTMLElement).style.transform = "translateY(-3px)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = "var(--border)";
              (e.currentTarget as HTMLElement).style.transform = "translateY(0)";
            }}
          >
            <div
              style={{
                position: "absolute",
                top: -30,
                right: -30,
                width: 100,
                height: 100,
                borderRadius: "50%",
                background: "rgba(0, 207, 255, 0.08)",
                filter: "blur(20px)",
              }}
            />
            <div style={{ fontSize: 28, marginBottom: 14 }}>🔥</div>
            <div
              className="pill"
              style={{
                marginBottom: 10,
                background: "rgba(0,207,255,0.1)",
                color: "#00cfff",
                borderColor: "rgba(0,207,255,0.2)",
              }}
            >
              Body Composition
            </div>
            <h2
              style={{
                fontFamily: "Syne, sans-serif",
                fontSize: 22,
                fontWeight: 700,
                marginBottom: 8,
              }}
            >
              CUT
            </h2>
            <p style={{ color: "var(--muted)", fontSize: 13, lineHeight: 1.6 }}>
              Forecast body fat %, lean muscle mass, and definition score (1–5) across 12 months of
              cutting.
            </p>
          </div>
        </Link>
      </div>
    </main>
  );
}
