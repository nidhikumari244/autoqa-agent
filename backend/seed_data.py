import sqlite3
import uuid
from datetime import datetime, timezone

def seed():
    conn = sqlite3.connect("autoqa.db")
    c = conn.cursor()

    # 1. Wikipedia Knowledge Portal
    c.execute("SELECT id FROM projects WHERE name = 'Wikipedia Knowledge Portal'")
    wiki_proj = c.fetchone()
    if not wiki_proj:
        wiki_id = str(uuid.uuid4())
        c.execute("""
            INSERT INTO projects (id, name, base_url, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (wiki_id, "Wikipedia Knowledge Portal", "https://en.wikipedia.org",
              "Autonomous navigation, search queries, knowledge extraction, and layout verification",
              datetime.now(timezone.utc), datetime.now(timezone.utc)))
    else:
        wiki_id = wiki_proj[0]

    # Seed scenarios for Wikipedia
    scenarios_wiki = [
        ("Search Artificial Intelligence & Verify Headline",
         "Find search input, query 'Artificial intelligence', and verify the page heading displays 'Artificial intelligence'.",
         "Heading element with text 'Artificial intelligence' is visible", 8),
        ("Verify Multi-Language Navigation & French Edition",
         "Locate the languages list or search bar, navigate to the French Wikipedia portal ('Français'), and assert the main banner text.",
         "Page URL contains 'fr.wikipedia.org' and portal banner is displayed", 6),
    ]

    for title, prompt, expected, max_s in scenarios_wiki:
        c.execute("SELECT id FROM test_scenarios WHERE project_id = ? AND title = ?", (wiki_id, title))
        if not c.fetchone():
            c.execute("""
                INSERT INTO test_scenarios (id, project_id, title, goal_prompt, expected_outcome, max_steps, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), wiki_id, title, prompt, expected, max_s, datetime.now(timezone.utc)))

    # 2. ShopFlow E-Commerce & Checkout Suite (Playwright Todo / Demo App)
    c.execute("SELECT id FROM projects WHERE name = 'ShopFlow E-Commerce & Checkout Suite'")
    shop_proj = c.fetchone()
    if not shop_proj:
        shop_id = str(uuid.uuid4())
        c.execute("""
            INSERT INTO projects (id, name, base_url, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (shop_id, "ShopFlow E-Commerce & Checkout Suite", "https://demo.playwright.dev/todomvc",
              "Production E2E verification of item selection, item count assertions, and state management",
              datetime.now(timezone.utc), datetime.now(timezone.utc)))
    else:
        shop_id = shop_proj[0]

    scenarios_shop = [
        ("Add Cart Items & Assert Counter Badge",
         "Find the input field, add 'High Performance Cloud Server' then press Enter, then add 'SSL Enterprise Certificate' then press Enter, and assert that the item counter shows '2 items left'.",
         "Element with text '2 items left' is visible", 10),
        ("Complete Item Checkout & Verify Filter Toggle",
         "Add an item 'Priority Delivery', click the toggle button to mark it completed, click 'Completed' filter, and verify the item is visible in completed list.",
         "Completed list displays marked item", 8),
    ]

    for title, prompt, expected, max_s in scenarios_shop:
        c.execute("SELECT id FROM test_scenarios WHERE project_id = ? AND title = ?", (shop_id, title))
        if not c.fetchone():
            c.execute("""
                INSERT INTO test_scenarios (id, project_id, title, goal_prompt, expected_outcome, max_steps, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), shop_id, title, prompt, expected, max_s, datetime.now(timezone.utc)))

    # 3. Hacker News & Tech Insights (Real Live Site)
    c.execute("SELECT id FROM projects WHERE name = 'HackerNews Aggregator'")
    hn_proj = c.fetchone()
    if not hn_proj:
        hn_id = str(uuid.uuid4())
        c.execute("""
            INSERT INTO projects (id, name, base_url, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (hn_id, "HackerNews Aggregator", "https://news.ycombinator.com",
              "Regression suite for live story feed, navigation pagination, and search queries",
              datetime.now(timezone.utc), datetime.now(timezone.utc)))
    else:
        hn_id = hn_proj[0]

    scenarios_hn = [
        ("Verify Top Story Navigation & Comments Link",
         "Verify the orange header navbar is visible, find the first story link and ensure story title is displayed with comments link.",
         "Top story title and comments anchor are visible", 6),
    ]

    for title, prompt, expected, max_s in scenarios_hn:
        c.execute("SELECT id FROM test_scenarios WHERE project_id = ? AND title = ?", (hn_id, title))
        if not c.fetchone():
            c.execute("""
                INSERT INTO test_scenarios (id, project_id, title, goal_prompt, expected_outcome, max_steps, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), hn_id, title, prompt, expected, max_s, datetime.now(timezone.utc)))

    conn.commit()
    conn.close()
    print("Database successfully seeded with enterprise test suites!")

if __name__ == "__main__":
    seed()
