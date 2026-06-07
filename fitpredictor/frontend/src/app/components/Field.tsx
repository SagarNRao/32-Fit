"use client";

interface FieldProps {
  label: string;
  children: React.ReactNode;
}

export function Field({ label, children }: FieldProps) {
  return (
    <div>
      <div className="label">{label}</div>
      {children}
    </div>
  );
}

interface GridProps {
  cols?: number;
  children: React.ReactNode;
}

export function Grid({ cols = 2, children }: GridProps) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(${cols}, 1fr)`,
        gap: 16,
      }}
    >
      {children}
    </div>
  );
}
