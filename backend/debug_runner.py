import asyncio
import traceback
from app.engine.runner import MasterTestRunner
from app.core.database import AsyncSessionLocal
from app.models.test_run import TestRun
from sqlalchemy import select

async def debug():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(TestRun).where(TestRun.id.like('b4dae77f%')))
        r = res.first()
        scenario_id = r[0].scenario_id
        
        # Create a new test run to test execution
        new_run = TestRun(scenario_id=scenario_id, status="PENDING")
        db.add(new_run)
        await db.commit()
        await db.refresh(new_run)
        test_id = new_run.id

    print("Testing runner for run_id:", test_id)
    runner = MasterTestRunner(run_id=test_id)
    try:
        await runner.execute()
    except Exception as e:
        print("EXCEPTION CAUGHT DIRECTLY:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug())
