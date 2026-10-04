import asyncio
import httpx
import sqlite3
import time

async def test():
    async with httpx.AsyncClient() as client:
        # Trigger run
        r = await client.post('http://localhost:8000/api/v1/runs/trigger', json={
            'scenario_id': '05e277a4-8ddb-47e0-b3fb-1f6166a93d8a'
        })
        run_data = r.json()
        run_id = run_data['id']
        print(f"[+] Triggered Run ID: {run_id}")
        
        # Poll for completion (up to 20 seconds)
        for i in range(20):
            await asyncio.sleep(1)
            conn = sqlite3.connect("autoqa.db")
            cur = conn.cursor()
            cur.execute("SELECT status, error_summary, duration_ms, generated_code_python FROM test_runs WHERE id = ?", (run_id,))
            row = cur.fetchone()
            conn.close()
            status, err, duration, py_code = row
            print(f"[{i+1}s] Status: {status}")
            if status in ["PASSED", "FAILED", "TIMED_OUT"]:
                print(f"Final Status: {status}")
                print(f"Duration: {duration}ms")
                print(f"Error / Summary: {err}")
                if py_code:
                    print("Generated Python Snippet:\n", py_code[:200], "...")
                return
        print("Timed out polling.")

if __name__ == "__main__":
    asyncio.run(test())
