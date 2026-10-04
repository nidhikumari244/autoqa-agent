from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.schemas.actions import BrowserAction

class InteractiveElement(BaseModel):
    id: int
    tag: str
    text: str
    role: Optional[str] = None
    aria_label: Optional[str] = None
    placeholder: Optional[str] = None
    name: Optional[str] = None
    selector: str
    bounding_box: Dict[str, float]

class DOMObservation(BaseModel):
    url: str
    title: str
    interactive_elements: List[InteractiveElement]
    compact_text_summary: str
    screenshot_base64: Optional[str] = None
