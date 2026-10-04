from enum import Enum
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    HOVER = "hover"
    SCROLL = "scroll"
    KEY_PRESS = "key_press"
    ASSERT_VISIBLE = "assert_visible"
    WAIT = "wait"
    FINISH = "finish"

class BrowserAction(BaseModel):
    action_type: ActionType = Field(..., description="The type of browser action to perform.")
    target_id: Optional[int] = Field(None, description="Numeric element ID assigned on the annotated interactive map.")
    selector: Optional[str] = Field(None, description="Fallback CSS selector or text locator if target_id is unavailable.")
    text: Optional[str] = Field(None, description="Input string for 'fill' or key name for 'key_press'.")
    url: Optional[str] = Field(None, description="Destination URL for 'navigate'.")
    direction: Optional[str] = Field("down", description="Direction for 'scroll' (up, down, top, bottom).")
    amount: Optional[int] = Field(500, description="Pixel scroll distance.")
    assertion_text: Optional[str] = Field(None, description="Expected text or message to assert on the page.")
    status: Optional[str] = Field("PASSED", description="Result for 'finish' action: PASSED or FAILED.")
    summary: Optional[str] = Field(None, description="Final outcome or bug description for 'finish'.")

class AgentStepDecision(BaseModel):
    thought: str = Field(..., description="High-level reasoning about current page state, goal progress, and next intent.")
    action: BrowserAction = Field(..., description="Atomic action to execute on the browser.")
