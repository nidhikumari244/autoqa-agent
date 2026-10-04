import sqlite3
import json

conn = sqlite3.connect("autoqa.db")
cursor = conn.cursor()
cursor.execute("SELECT id, status, error_summary, duration_ms FROM test_runs ORDER BY created_at DESC LIMIT 5")
rows = cursor.fetchall()
for r in rows:
    print("RUN:", r[0][:8], "STATUS:", r[1])
    print("ERROR:", r[2])
    print("DURATION:", r[3])
    print("---")
conn.close()
