export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
export const API_BASE = process.env.NEXT_PUBLIC_API_URL || `${BACKEND_URL}/api/v1`;
export const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || `${BACKEND_URL.replace(/^http/, "ws")}/api/v1/ws`;

export interface Project {
  id: string;
  name: string;
  base_url: string;
  description?: string;
  created_at: string;
}

export interface TestScenario {
  id: string;
  project_id: string;
  title: string;
  goal_prompt: string;
  expected_outcome?: string;
  max_steps: number;
  created_at: string;
}

export interface TestStep {
  id: string;
  step_number: number;
  action_type: string;
  thought?: string;
  action_payload?: any;
  screenshot_url?: string;
  execution_time_ms?: number;
  status: string;
}

export interface TestRun {
  id: string;
  scenario_id: string;
  status: "PENDING" | "RUNNING" | "PASSED" | "FAILED" | "TIMED_OUT";
  total_steps: number;
  duration_ms?: number;
  generated_code_python?: string;
  generated_code_ts?: string;
  error_summary?: string;
  report_pdf_path?: string;
  created_at: string;
  finished_at?: string;
  steps: TestStep[];
}

export const api = {
  async getHealth() {
    const res = await fetch(`${BACKEND_URL}/health`);
    return res.json();
  },

  async getProjects(): Promise<Project[]> {
    const res = await fetch(`${API_BASE}/projects/`);
    if (!res.ok) throw new Error("Failed to fetch projects");
    return res.json();
  },

  async createProject(data: { name: string; base_url: string; description?: string }): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create project");
    return res.json();
  },

  async getScenarios(projectId: string): Promise<TestScenario[]> {
    const res = await fetch(`${API_BASE}/scenarios/project/${projectId}`);
    if (!res.ok) throw new Error("Failed to fetch scenarios");
    return res.json();
  },

  async createScenario(projectId: string, data: { title: string; goal_prompt: string; expected_outcome?: string; max_steps?: number }): Promise<TestScenario> {
    const res = await fetch(`${API_BASE}/scenarios/${projectId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create scenario");
    return res.json();
  },

  async triggerRun(scenarioId: string): Promise<TestRun> {
    const res = await fetch(`${API_BASE}/runs/trigger`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_id: scenarioId }),
    });
    if (!res.ok) throw new Error("Failed to trigger run");
    return res.json();
  },

  async getRun(runId: string): Promise<TestRun> {
    const res = await fetch(`${API_BASE}/runs/${runId}`);
    if (!res.ok) throw new Error("Failed to fetch run details");
    return res.json();
  },

  async listRunsForScenario(scenarioId: string): Promise<TestRun[]> {
    const res = await fetch(`${API_BASE}/runs/scenario/${scenarioId}`);
    if (!res.ok) throw new Error("Failed to fetch scenario runs");
    return res.json();
  },

  async getAllRuns(limit = 30): Promise<TestRun[]> {
    const res = await fetch(`${API_BASE}/runs/?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch all runs");
    return res.json();
  },

  connectWebSocket(runId: string, onMessage: (msg: any) => void) {
    const ws = new WebSocket(`${WS_BASE}/runs/${runId}`);
    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        onMessage(parsed);
      } catch (e) {
        console.error("WS Parse error", e);
      }
    };
    return ws;
  }
};
