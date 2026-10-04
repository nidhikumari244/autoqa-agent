import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.project import TestScenario
from app.models.test_run import TestRun, TestRunStep
from app.schemas.project import TestRunCreate, TestRunResponse
from app.engine.runner import MasterTestRunner

router = APIRouter()

@router.post("/trigger", response_model=TestRunResponse)
async def trigger_run(
    payload: TestRunCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    # Verify scenario exists
    result = await db.execute(select(TestScenario).where(TestScenario.id == payload.scenario_id))
    scenario = result.scalar_one_or_none()
    if not scenario:
        raise HTTPException(status_code=404, detail="Test scenario not found")

    new_run = TestRun(
        scenario_id=scenario.id,
        status="PENDING"
    )
    db.add(new_run)
    await db.commit()
    await db.refresh(new_run)

    # Launch autonomous runner in background
    runner = MasterTestRunner(run_id=new_run.id)
    background_tasks.add_task(runner.execute)

    # Reload with empty steps relation
    run_response = await db.execute(
        select(TestRun)
        .options(selectinload(TestRun.steps))
        .where(TestRun.id == new_run.id)
    )
    return run_response.scalar_one()

@router.get("/", response_model=List[TestRunResponse])
async def list_all_runs(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TestRun)
        .options(selectinload(TestRun.steps))
        .order_by(TestRun.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/{run_id}", response_model=TestRunResponse)
async def get_run_details(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TestRun)
        .options(selectinload(TestRun.steps))
        .where(TestRun.id == run_id)
    )
    test_run = result.scalar_one_or_none()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    return test_run

@router.get("/scenario/{scenario_id}", response_model=List[TestRunResponse])
async def list_runs_for_scenario(scenario_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TestRun)
        .options(selectinload(TestRun.steps))
        .where(TestRun.scenario_id == scenario_id)
        .order_by(TestRun.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{run_id}/script/{lang}")
async def download_script(run_id: str, lang: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TestRun).where(TestRun.id == run_id))
    test_run = result.scalar_one_or_none()
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")

    if lang.lower() == "python":
        content = test_run.generated_code_python or "# No script generated"
        media_type = "text/x-python"
        filename = f"test_{run_id[:8]}.py"
    elif lang.lower() in ["ts", "typescript"]:
        content = test_run.generated_code_ts or "// No script generated"
        media_type = "text/typescript"
        filename = f"test_{run_id[:8]}.spec.ts"
    else:
        raise HTTPException(status_code=400, detail="Supported languages: python, typescript")

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
