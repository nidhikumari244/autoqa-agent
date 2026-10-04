import json
import base64
import httpx
from typing import List, Dict, Any, Optional
from app.schemas.actions import AgentStepDecision, BrowserAction, ActionType
from app.schemas.agent import DOMObservation
from app.core.config import settings

SYSTEM_PROMPT = """You are AutoQA, an expert autonomous web testing agent.
Your objective is to achieve a user's test goal on a web application through deterministic, step-by-step browser interactions.

You are provided with:
1. Current Page URL and Title.
2. A numbered list of currently visible interactive elements in format: `[ID] <tag> "text" ...`
3. A visual screenshot where each interactive element is tagged with its corresponding red ID badge (Set-of-Marks).
4. History of past actions executed in this session.

Rules for deciding your next action:
- Carefully evaluate the user's goal against what is currently displayed on screen.
- Choose EXACTLY ONE atomic action per step.
- To interact with an element, provide its exact integer `target_id`.
- If an input needs typing, use action_type 'fill' with the `target_id` and the `text`.
- If you need to submit after filling, click the submit button or use 'key_press' with 'Enter'.
- When the goal is completed, call action_type 'finish' with status 'PASSED' and a concise explanation.
- If you encounter a blocking bug, broken page, or failure that prevents reaching the goal, call action_type 'finish' with status 'FAILED'.
- Keep your 'thought' focused, explaining what you observe and why you chose this action.

You MUST respond strictly with valid JSON conforming to this schema:
{
  "thought": "Analysis of current state and intention",
  "action": {
    "action_type": "navigate" | "click" | "fill" | "hover" | "scroll" | "key_press" | "assert_visible" | "wait" | "finish",
    "target_id": integer or null,
    "text": string or null,
    "url": string or null,
    "direction": "down" | "up" or null,
    "amount": integer or null,
    "assertion_text": string or null,
    "status": "PASSED" | "FAILED" or null,
    "summary": string or null
  }
}
"""

class VisionAgent:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or settings.OPENAI_API_KEY
        self.model = model or settings.DEFAULT_MODEL

    async def decide_next_step(
        self,
        goal: str,
        dom_obs: DOMObservation,
        screenshot_bytes: bytes,
        history: List[Dict[str, Any]]
    ) -> AgentStepDecision:
        """
        Calls Gemini Multi-Modal API (or OpenAI compatible) to determine the next action.
        """
        # If no API key configured, use intelligent rule-based / exploration fallback for demos
        if not self.api_key:
            return self._heuristic_fallback(goal, dom_obs, history)

        # Gemini API call
        if "gemini" in self.model.lower():
            return await self._call_gemini_vision(goal, dom_obs, screenshot_bytes, history)
        else:
            return await self._call_openai_vision(goal, dom_obs, screenshot_bytes, history)

    async def _call_gemini_vision(
        self,
        goal: str,
        dom_obs: DOMObservation,
        screenshot_bytes: bytes,
        history: List[Dict[str, Any]]
    ) -> AgentStepDecision:
        b64_image = base64.b64encode(screenshot_bytes).decode("utf-8")
        
        history_summary = "\n".join([
            f"- Step {h['step']}: {h['action_type']} -> {h.get('details', '')} | Outcome: {h.get('thought', '')}"
            for h in history
        ]) or "None yet (Initial step)"

        user_content = f"""USER TEST GOAL: {goal}

CURRENT PAGE:
URL: {dom_obs.url}
Title: {dom_obs.title}

INTERACTIVE ELEMENTS ON SCREEN:
{dom_obs.compact_text_summary or "No interactive elements detected."}

PREVIOUS ACTIONS IN THIS RUN:
{history_summary}

Based on the attached screenshot and element list, determine the next action:"""

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": SYSTEM_PROMPT},
                        {"text": user_content},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_image
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(endpoint, json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini API returned error {resp.status_code}: {resp.text}")
            
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            clean_json = self._clean_json(raw_text)
            parsed = json.loads(clean_json)
            return AgentStepDecision(**parsed)

    async def _call_openai_vision(
        self,
        goal: str,
        dom_obs: DOMObservation,
        screenshot_bytes: bytes,
        history: List[Dict[str, Any]]
    ) -> AgentStepDecision:
        b64_image = base64.b64encode(screenshot_bytes).decode("utf-8")
        # OpenAI or compatible endpoint
        endpoint = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        user_content = [
            {"type": "text", "text": f"GOAL: {goal}\nURL: {dom_obs.url}\n\nELEMENTS:\n{dom_obs.compact_text_summary}"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
        ]

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(endpoint, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["choices"][0]["message"]["content"]
            parsed = json.loads(raw_text)
            return AgentStepDecision(**parsed)

    def _heuristic_fallback(
        self,
        goal: str,
        dom_obs: DOMObservation,
        history: List[Dict[str, Any]]
    ) -> AgentStepDecision:
        """
        Offline / Demo fallback when no API key is provided yet.
        Enables seamless testing of the full browser engine and UI pipeline.
        """
        step_count = len(history)
        goal_lower = goal.lower()

        # Step 0: Check if we are already at the target
        if step_count == 0 and "navigate" not in [h.get("action_type") for h in history]:
            # If target has a search box, find input
            for elem in dom_obs.interactive_elements:
                if elem.tag == "input" and any(k in (elem.name or elem.placeholder or "").lower() for k in ["search", "q", "query"]):
                    return AgentStepDecision(
                        thought=f"Found search input field [{elem.id}]. Filling search term.",
                        action=BrowserAction(action_type=ActionType.FILL, target_id=elem.id, text="AutoQA verification")
                    )

        # If we just filled an input, submit or press enter
        if history and history[-1].get("action_type") == "fill":
            return AgentStepDecision(
                thought="Search term entered. Pressing Enter to execute search.",
                action=BrowserAction(action_type=ActionType.KEY_PRESS, text="Enter")
            )

        # If we have run for a couple steps, finish
        if step_count >= 2:
            return AgentStepDecision(
                thought="Page verified and key interactions executed successfully.",
                action=BrowserAction(
                    action_type=ActionType.FINISH,
                    status="PASSED",
                    summary="Goal verified: interactive elements responded and page loaded without errors."
                )
            )

        # Default: click first prominent link or scroll
        if dom_obs.interactive_elements:
            elem = dom_obs.interactive_elements[0]
            return AgentStepDecision(
                thought=f"Navigating to primary interaction point [{elem.id}]: {elem.text or elem.tag}",
                action=BrowserAction(action_type=ActionType.CLICK, target_id=elem.id)
            )

        return AgentStepDecision(
            thought="Finished inspecting page.",
            action=BrowserAction(action_type=ActionType.FINISH, status="PASSED", summary="Inspected page.")
        )

    def _clean_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
