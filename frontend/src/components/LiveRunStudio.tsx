import React, { useState, useEffect } from "react";
import { 
  Play, CheckCircle2, XCircle, Clock, Copy, Check, Download, 
  Terminal, Code2, FileText, ChevronRight, Sparkles, Eye, ArrowRight 
} from "lucide-react";
import { api, BACKEND_URL, TestRun } from "@/lib/api";

interface Props {
  runId: string;
  onClose: () => void;
}

export const LiveRunStudio: React.FC<Props> = ({ runId, onClose }) => {
  const [run, setRun] = useState<TestRun | null>(null);
  const [currentScreenshot, setCurrentScreenshot] = useState<string | null>(null);
  const [currentUrl, setCurrentUrl] = useState<string>("");
  const [agentThinking, setAgentThinking] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"timeline" | "code" | "report">("timeline");
  const [codeLang, setCodeLang] = useState<"python" | "typescript">("python");
  const [copied, setCopied] = useState(false);
  const [elementsCount, setElementsCount] = useState<number>(0);

  useEffect(() => {
    // 1. Initial fetch of run details
    api.getRun(runId).then((data) => {
      setRun(data);
      if (data.steps && data.steps.length > 0) {
        const lastStep = data.steps[data.steps.length - 1];
        if (lastStep.screenshot_url) {
          setCurrentScreenshot(`${BACKEND_URL}${lastStep.screenshot_url}`);
        }
      }
    });

    // 2. Connect WebSocket
    const ws = api.connectWebSocket(runId, (msg) => {
      if (msg.type === "SCREENSHOT_UPDATE") {
        setCurrentScreenshot(`data:image/jpeg;base64,${msg.screenshot_b64}`);
        if (msg.url) setCurrentUrl(msg.url);
        if (msg.interactive_elements_count !== undefined) setElementsCount(msg.interactive_elements_count);
      } else if (msg.type === "AGENT_THINKING") {
        setAgentThinking(msg.message);
      } else if (msg.type === "STEP_DECISION") {
        setAgentThinking(`Action: ${msg.action_type.toUpperCase()} • ${msg.thought}`);
      } else if (msg.type === "STEP_COMPLETED") {
        // Refresh run state to get updated steps
        api.getRun(runId).then(setRun);
      } else if (msg.type === "RUN_FINISHED") {
        api.getRun(runId).then(setRun);
        setAgentThinking("");
      } else if (msg.type === "RUN_ERROR") {
        api.getRun(runId).then(setRun);
        setAgentThinking(`Error: ${msg.error || "Run failed"}`);
      }
    });

    return () => {
      ws.close();
    };
  }, [runId]);

  const copyCode = () => {
    const code = codeLang === "python" ? run?.generated_code_python : run?.generated_code_ts;
    if (code) {
      navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getStatusBadge = () => {
    if (!run) return null;
    if (run.status === "RUNNING") {
      return (
        <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-semibold animate-pulse">
          <span className="w-2 h-2 rounded-full bg-amber-400"></span>
          <span>EXECUTING AGENT</span>
        </span>
      );
    }
    if (run.status === "PASSED") {
      return (
        <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>VERIFIED PASSED</span>
        </span>
      );
    }
    return (
      <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-xs font-semibold">
        <XCircle className="w-3.5 h-3.5" />
        <span>{run.status}</span>
      </span>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-[#080d19] text-slate-100">
      {/* Top Navigation Bar */}
      <div className="border-b border-slate-800 bg-[#0d1424] px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onClose}
            className="text-xs font-medium text-slate-400 hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-slate-800 transition flex items-center space-x-1"
          >
            <span>&larr; Exit Studio</span>
          </button>
          <div className="h-4 w-px bg-slate-800"></div>
          <div>
            <h2 className="text-sm font-bold text-white flex items-center space-x-2">
              <span>Run ID: {runId.slice(0, 8)}</span>
              {getStatusBadge()}
            </h2>
            <p className="text-[11px] text-slate-400 truncate max-w-md">
              {currentUrl || "Initializing browser session..."}
            </p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center bg-slate-900/80 p-1 rounded-xl border border-slate-800 space-x-1">
          <button
            onClick={() => setActiveTab("timeline")}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === "timeline" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Agent Steps ({run?.steps?.length || 0})</span>
          </button>
          <button
            onClick={() => setActiveTab("code")}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === "code" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Generated Code</span>
          </button>
          <button
            onClick={() => setActiveTab("report")}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === "report" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Audit Report</span>
          </button>
        </div>
      </div>

      {/* Main Split Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Side: Live Browser Screencast */}
        <div className="flex-1 flex flex-col border-r border-slate-800 bg-[#090e1a] p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
                <Eye className="w-3.5 h-3.5 text-indigo-400" />
                <span>Live Browser Canvas (Set-of-Marks Grounding)</span>
              </span>
              {elementsCount > 0 && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {elementsCount} Interactive Nodes
                </span>
              )}
            </div>

            {agentThinking && (
              <div className="flex items-center space-x-2 px-3 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs animate-pulse max-w-sm truncate">
                <Sparkles className="w-3 h-3 text-indigo-400 shrink-0" />
                <span className="truncate">{agentThinking}</span>
              </div>
            )}
          </div>

          <div className="flex-1 rounded-xl border border-slate-800 bg-black/50 overflow-hidden flex items-center justify-center relative shadow-inner">
            {currentScreenshot ? (
              <img
                src={currentScreenshot}
                alt="Live Browser Screencast"
                className="w-full h-full object-contain"
              />
            ) : (
              <div className="text-center p-6 text-slate-500 space-y-2">
                <div className="w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p className="text-xs font-medium">Launching isolated Chromium sandbox...</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Tab Content */}
        <div className="w-[480px] bg-[#0c1220] flex flex-col overflow-hidden">
          {activeTab === "timeline" && (
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Step Execution Timeline
                </h3>
                <span className="text-xs text-slate-500 font-mono">
                  {run?.duration_ms ? `${(run.duration_ms / 1000).toFixed(1)}s elapsed` : ""}
                </span>
              </div>

              {run?.steps && run.steps.length > 0 ? (
                run.steps.map((step) => (
                  <div
                    key={step.id}
                    className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 space-y-2 hover:border-slate-700 transition"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="w-5 h-5 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-mono text-[11px] font-bold flex items-center justify-center">
                          {step.step_number}
                        </span>
                        <span className="text-xs font-bold text-white uppercase tracking-wide">
                          {step.action_type}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {step.execution_time_ms}ms
                      </span>
                    </div>

                    {step.thought && (
                      <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-2 rounded-lg border border-slate-800/80">
                        {step.thought}
                      </p>
                    )}

                    {step.action_payload && (
                      <div className="text-[11px] text-slate-400 font-mono flex items-center space-x-1.5 truncate">
                        <ChevronRight className="w-3 h-3 text-slate-500 shrink-0" />
                        <span className="truncate">
                          Target: {step.action_payload.selector || `Node #${step.action_payload.target_id || "-"}`}
                          {step.action_payload.text && ` • "${step.action_payload.text}"`}
                        </span>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-16 text-slate-500 text-xs">
                  Awaiting first execution step...
                </div>
              )}
            </div>
          )}

          {activeTab === "code" && (
            <div className="flex-1 flex flex-col p-4 overflow-hidden">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
                <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-lg border border-slate-800">
                  <button
                    onClick={() => setCodeLang("python")}
                    className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                      codeLang === "python" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                    }`}
                  >
                    pytest (Python)
                  </button>
                  <button
                    onClick={() => setCodeLang("typescript")}
                    className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                      codeLang === "typescript" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-white"
                    }`}
                  >
                    Playwright (TS)
                  </button>
                </div>

                <button
                  onClick={copyCode}
                  className="flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? "Copied!" : "Copy Code"}</span>
                </button>
              </div>

              <div className="flex-1 bg-slate-950/80 rounded-xl border border-slate-800 p-3 font-mono text-xs overflow-auto text-slate-300 leading-relaxed select-all">
                <pre>
                  {codeLang === "python"
                    ? run?.generated_code_python || "# Script generating after run completes..."
                    : run?.generated_code_ts || "// Script generating after run completes..."}
                </pre>
              </div>
            </div>
          )}

          {activeTab === "report" && (
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div className="pb-3 border-b border-slate-800">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Audit Report & Verification
                </h3>
              </div>

              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Status</span>
                  <span className="font-semibold text-xs text-emerald-400">{run?.status}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Total Steps Recorded</span>
                  <span className="font-semibold text-xs text-white">{run?.steps?.length || 0}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Total Run Time</span>
                  <span className="font-semibold text-xs text-white">
                    {run?.duration_ms ? `${(run.duration_ms / 1000).toFixed(2)}s` : "-"}
                  </span>
                </div>
                {run?.error_summary && (
                  <div className="pt-2 border-t border-slate-800">
                    <span className="text-xs text-rose-400 block mb-1 font-medium">Outcome Summary:</span>
                    <p className="text-xs text-slate-300 bg-rose-500/10 border border-rose-500/20 p-2.5 rounded-lg">
                      {run.error_summary}
                    </p>
                  </div>
                )}
              </div>

              {run?.report_pdf_path && (
                <a
                  href={`${BACKEND_URL}${run.report_pdf_path}`}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition shadow-lg shadow-indigo-600/20"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Formal PDF Report</span>
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
