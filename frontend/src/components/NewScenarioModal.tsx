import React, { useState } from "react";
import { X, PlayCircle, Sparkles } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { title: string; goal_prompt: string; expected_outcome?: string; max_steps?: number }) => Promise<void>;
}

export const NewScenarioModal: React.FC<Props> = ({ isOpen, onClose, onSubmit }) => {
  const [title, setTitle] = useState("");
  const [goalPrompt, setGoalPrompt] = useState("");
  const [expectedOutcome, setExpectedOutcome] = useState("");
  const [maxSteps, setMaxSteps] = useState(20);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !goalPrompt) return;
    setLoading(true);
    try {
      await onSubmit({
        title,
        goal_prompt: goalPrompt,
        expected_outcome: expectedOutcome,
        max_steps: maxSteps
      });
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-[#111827] border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl animate-in fade-in zoom-in-95 duration-150">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <PlayCircle className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">Declare Test Scenario</h2>
              <p className="text-xs text-slate-400">Specify what you want the autonomous agent to verify</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Scenario Title</label>
            <input
              type="text"
              placeholder="e.g. Verify User Checkout Flow with Discount Code"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full bg-slate-900/80 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-medium text-slate-300">Goal Prompt (Plain English)</label>
              <span className="text-[11px] text-indigo-400 flex items-center space-x-1">
                <Sparkles className="w-3 h-3" />
                <span>AI Grounded</span>
              </span>
            </div>
            <textarea
              placeholder="e.g. Search for 'backpack', click the first result, click 'Add to Cart', and verify that the checkout summary shows 1 item with total price > $0."
              value={goalPrompt}
              onChange={(e) => setGoalPrompt(e.target.value)}
              rows={3}
              required
              className="w-full bg-slate-900/80 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition resize-none"
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="col-span-2">
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Expected Assertion (Optional)</label>
              <input
                type="text"
                placeholder="e.g. Order Summary or Thank you for your purchase"
                value={expectedOutcome}
                onChange={(e) => setExpectedOutcome(e.target.value)}
                className="w-full bg-slate-900/80 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Max Steps</label>
              <input
                type="number"
                min={3}
                max={50}
                value={maxSteps}
                onChange={(e) => setMaxSteps(Number(e.target.value))}
                className="w-full bg-slate-900/80 border border-slate-700/80 rounded-lg px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 transition"
              />
            </div>
          </div>

          <div className="flex items-center justify-end space-x-2.5 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition disabled:opacity-50"
            >
              {loading ? "Creating..." : "Save Scenario"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
