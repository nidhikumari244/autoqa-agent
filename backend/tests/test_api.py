import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import httpx
from app.main import app
from app.core.database import init_db

async def test_api_endpoints():
    await init_db()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        resp = await client.get("/health")
        assert resp.status_code == 200, f"Health check failed: {resp.text}"
        data = resp.json()
        assert data["status"] == "online"
        print("[OK] Health endpoint passed:", data)

        # 2. Create Project
        resp = await client.post("/api/v1/projects/", json={
            "name": "E-Commerce Smoke Suite",
            "base_url": "https://example.com",
            "description": "Autonomous verification of checkout and navigation"
        })
        assert resp.status_code == 200, f"Create project failed: {resp.text}"
        proj = resp.json()
        proj_id = proj["id"]
        print(f"[OK] Created Project: {proj['name']} (ID: {proj_id})")

        # 3. Create Test Scenario
        resp = await client.post(f"/api/v1/scenarios/{proj_id}", json={
            "title": "Homepage Link Verification",
            "goal_prompt": "Click the More information link and verify target page loads.",
            "expected_outcome": "Navigates to IANA example domains page",
            "max_steps": 5
        })
        assert resp.status_code == 200, f"Create scenario failed: {resp.text}"
        scenario = resp.json()
        scenario_id = scenario["id"]
        print(f"[OK] Created Scenario: {scenario['title']} (ID: {scenario_id})")

        # 4. Trigger Run (Async)
        resp = await client.post("/api/v1/runs/trigger", json={
            "scenario_id": scenario_id
        })
        assert resp.status_code == 200, f"Trigger run failed: {resp.text}"
        run_data = resp.json()
        run_id = run_data["id"]
        print(f"[OK] Triggered Run: ID {run_id}, Initial Status: {run_data['status']}")

        # Give the background runner 4 seconds to execute
        await asyncio.sleep(4)

        # 5. Check Run Status
        resp = await client.get(f"/api/v1/runs/{run_id}")
        assert resp.status_code == 200
        run_status = resp.json()
        print(f"[OK] Run Progress Status: {run_status['status']}, Steps Recorded: {len(run_status.get('steps', []))}")

    print("\n==============================")
    print("ALL API ENDPOINTS PASSED!")
    print("==============================")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
