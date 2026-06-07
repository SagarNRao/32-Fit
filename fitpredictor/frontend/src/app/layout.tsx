import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "FitPredictor",
  description: "Predict your muscle growth and body composition changes",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
