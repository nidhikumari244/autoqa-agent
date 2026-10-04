import React, { useState } from "react";
import { X, Copy, Check, Download, Terminal, Code2 } from "lucide-react";
import { TestRun } from "@/lib/api";

interface CodePreviewModalProps {
  run: TestRun | null;
  scenarioTitle: string;
  isOpen: boolean;
  onClose: () => void;
}

export const CodePreviewModal: React.FC<CodePreviewModalProps> = ({
  run,
  scenarioTitle,
  isOpen,
  onClose,
}) => {
  const [lang, setLang] = useState<"python" | "typescript">("python");
  const [copied, setCopied] = useState(false);

  if (!isOpen || !run) return null;

  const code = lang === "python" ? run.generated_code_python : run.generated_code_ts;

  const handleCopy = () => {
    if (code) {
      navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (!code) return;
    const blob = new Blob([code], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = lang === "python" ? `test_${run.id.slice(0, 8)}.py` : `test_${run.id.slice(0, 8)}.spec.ts`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-4xl bg-[#0c1220] border border-slate-800 rounded-2xl shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Code2 className="w-4 h-4" />
                <span>Deterministic Code Synthesizer</span>
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                CI/CD Runnable
              </span>
            </div>
            <h3 className="text-base font-bold text-white truncate max-w-xl">
              {scenarioTitle}
            </h3>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Toolbar */}
        <div className="px-6 py-3 border-b border-slate-800 bg-[#090d18] flex items-center justify-between">
          <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setLang("python")}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                lang === "python"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              pytest-playwright (Python)
            </button>
            <button
              onClick={() => setLang("typescript")}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition ${
                lang === "typescript"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              @playwright/test (TypeScript)
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopy}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? "Copied!" : "Copy Spec"}</span>
            </button>
            <button
              onClick={handleDownload}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download File</span>
            </button>
          </div>
        </div>

        {/* Code Content */}
        <div className="flex-1 overflow-y-auto p-6 bg-[#070b14] font-mono text-xs text-slate-300">
          {code ? (
            <pre className="overflow-x-auto whitespace-pre leading-relaxed select-all">
              <code>{code}</code>
            </pre>
          ) : (
            <div className="text-center py-12 text-slate-500">
              No code generated for this test run. Run the autonomous agent to synthesize the spec.
            </div>
          )}
        </div>

        {/* Footer info */}
        <div className="px-6 py-3 border-t border-slate-800 bg-[#0c1220] flex items-center justify-between text-[11px] text-slate-400">
          <span>Run ID: <code className="text-indigo-400 font-mono">{run.id.slice(0, 8)}</code></span>
          <span>Zero external LLM calls required during CI/CD execution</span>
        </div>
      </div>
    </div>
  );
};
