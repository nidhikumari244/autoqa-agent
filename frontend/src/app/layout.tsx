import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AutoQA — Autonomous Browser Testing Agent",
  description: "Self-healing, multi-modal autonomous web QA agent and test code synthesizer",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0b0f19] text-slate-100 antialiased selection:bg-indigo-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
