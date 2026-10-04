import React, { useState, useEffect } from "react";
import { 
  Sparkles, Plus, Globe, ShieldCheck, GitBranch, Cpu, 
  ExternalLink, Layers, Terminal 
} from "lucide-react";
import { api } from "@/lib/api";

interface HeaderProps {
  onNewProject: () => void;
  onNewScenario: () => void;
  hasProjects: boolean;
  selectedEnvironment: string;
  onSelectEnvironment: (env: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  onNewProject,
  onNewScenario,
  hasProjects,
  selectedEnvironment,
  onSelectEnvironment,
}) => {
  const [engineStatus, setEngineStatus] = useState<"checking" | "online" | "offline">("checking");
  const [engineDetails, setEngineDetails] = useState<string>("Connecting...");

  useEffect(() => {
    let mounted = true;
    api.getHealth()
      .then((data) => {
        if (mounted) {
          setEngineStatus("online");
          setEngineDetails(`Engine: Online (${data.headless ? "Headless" : "Headed"} • ${data.default_model || "Gemini"})`);
        }
      })
      .catch(() => {
        if (mounted) {
          setEngineStatus("offline");
          setEngineDetails("Engine: Offline");
        }
      });
    return () => { mounted = false; };
  }, []);
  return (
    <header className="border-b border-slate-800/80 bg-[#0d1322]/95 backdrop-blur-md sticky top-0 z-40 px-6 py-3 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-lg shadow-black/20">
      {/* Left: Brand & Navigation */}
      <div className="flex items-center space-x-4">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 shrink-0">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-base font-bold tracking-tight text-white">AutoQA Studio</h1>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold">
              Enterprise v2.4
            </span>
            <div className="hidden sm:flex items-center space-x-1 text-[11px] text-slate-400 font-mono px-2 py-0.5 rounded-md bg-slate-800/60 border border-slate-700/50">
              <GitBranch className="w-3 h-3 text-slate-400" />
              <span>main: <span className="text-indigo-300">4f98a2e</span></span>
            </div>
          </div>
          <p className="text-[11px] text-slate-400">Autonomous Multi-Modal E2E Verification & Playwright Code Synthesizer</p>
        </div>
      </div>

      {/* Right: Environment, Engine Status, and Actions */}
      <div className="flex items-center flex-wrap gap-2.5">
        {/* Environment Picker */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs">
          <Layers className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={selectedEnvironment}
            onChange={(e) => onSelectEnvironment(e.target.value)}
            className="bg-transparent text-slate-300 font-semibold focus:outline-none cursor-pointer text-xs"
          >
            <option value="Production (v2.4)">Env: Production (v2.4)</option>
            <option value="Staging (v2.5-rc)">Env: Staging (v2.5-rc)</option>
            <option value="Local Sandbox">Env: Local Sandbox</option>
          </select>
        </div>

        {/* Engine Status */}
        <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold border ${
          engineStatus === "online" 
            ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
            : engineStatus === "offline"
            ? "bg-rose-500/10 border-rose-500/20 text-rose-400"
            : "bg-amber-500/10 border-amber-500/20 text-amber-400"
        }`}>
          <span className={`w-2 h-2 rounded-full ${
            engineStatus === "online" ? "bg-emerald-400 animate-pulse" : engineStatus === "offline" ? "bg-rose-400" : "bg-amber-400 animate-ping"
          }`}></span>
          <span>{engineDetails}</span>
        </div>

        <button
          onClick={onNewProject}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition border border-slate-700"
        >
          <Globe className="w-3.5 h-3.5 text-slate-400" />
          <span>New Target App</span>
        </button>

        {hasProjects && (
          <button
            onClick={onNewScenario}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white text-xs font-semibold shadow-md shadow-indigo-600/25 transition"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>New Test Scenario</span>
          </button>
        )}
      </div>
    </header>
  );
};
