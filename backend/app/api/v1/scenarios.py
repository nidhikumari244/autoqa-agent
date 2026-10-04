from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.project import TestScenario, Project
from app.schemas.project import ScenarioCreate, ScenarioResponse

router = APIRouter()

@router.post("/{project_id}", response_model=ScenarioResponse)
async def create_scenario(
    project_id: str,
    payload: ScenarioCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    scenario = TestScenario(
        project_id=project_id,
        title=payload.title,
        goal_prompt=payload.goal_prompt,
        expected_outcome=payload.expected_outcome,
        max_steps=payload.max_steps or 25
    )
    db.add(scenario)
    await db.commit()
    await db.refresh(scenario)
    return scenario

@router.get("/project/{project_id}", response_model=List[ScenarioResponse])
async def list_scenarios_for_project(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TestScenario)
        .where(TestScenario.project_id == project_id)
        .order_by(TestScenario.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(scenario_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TestScenario).where(TestScenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

@router.delete("/{scenario_id}")
async def delete_scenario(scenario_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TestScenario).where(TestScenario.id == scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    await db.delete(scenario)
    await db.commit()
    return {"message": "Scenario deleted successfully"}
