from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, computed_field

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str = Field(..., example="E-Commerce Store")
    base_url: str = Field(..., example="https://ecommerce.example.com")
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Test Scenario Schemas ---
class ScenarioBase(BaseModel):
    title: str = Field(..., example="User Checkout Flow")
    goal_prompt: str = Field(..., example="Add a product to cart and verify order summary displays correct price.")
    expected_outcome: Optional[str] = "Order summary matches total cart item value."
    max_steps: Optional[int] = 25

class ScenarioCreate(ScenarioBase):
    pass

class ScenarioResponse(ScenarioBase):
    id: str
    project_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Test Step Schemas ---
class TestStepResponse(BaseModel):
    id: str
    step_number: int
    action_type: str
    thought: Optional[str] = None
    action_payload: Optional[dict] = None
    screenshot_path: Optional[str] = None
    execution_time_ms: Optional[int] = None
    status: str

    @computed_field
    @property
    def screenshot_url(self) -> Optional[str]:
        return self.screenshot_path

    class Config:
        from_attributes = True

# --- Test Run Schemas ---
class TestRunCreate(BaseModel):
    scenario_id: str
    custom_instructions: Optional[str] = None
    headless: Optional[bool] = True

class TestRunResponse(BaseModel):
    id: str
    scenario_id: str
    status: str
    total_steps: Optional[int] = 0
    duration_ms: Optional[int] = None
    generated_code_python: Optional[str] = None
    generated_code_ts: Optional[str] = None
    error_summary: Optional[str] = None
    report_pdf_path: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None
    steps: List[TestStepResponse] = []

    class Config:
        from_attributes = True
