import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scenario_id = Column(String(36), ForeignKey("test_scenarios.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, RUNNING, PASSED, FAILED, TIMED_OUT
    duration_ms = Column(Integer, default=0)
    generated_code_python = Column(Text, nullable=True)
    generated_code_ts = Column(Text, nullable=True)
    error_summary = Column(Text, nullable=True)
    report_pdf_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at = Column(DateTime, nullable=True)

    scenario = relationship("TestScenario", back_populates="runs")
    steps = relationship("TestRunStep", back_populates="run", cascade="all, delete-orphan", order_by="TestRunStep.step_number")

class TestRunStep(Base):
    __tablename__ = "test_run_steps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(Integer, nullable=False)
    action_type = Column(String(50), nullable=False)
    thought = Column(Text, nullable=True)
    action_payload = Column(JSON, nullable=True)
    screenshot_path = Column(String(512), nullable=True)
    execution_time_ms = Column(Integer, default=0)
    status = Column(String(50), default="SUCCESS")  # SUCCESS, FAILED, RETRIED

    run = relationship("TestRun", back_populates="steps")
