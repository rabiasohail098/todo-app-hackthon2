"""Add guided_state columns to conversations table."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Check if columns exist first
    result = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'conversations' AND column_name IN ('guided_state', 'pending_task_json')
    """))
    existing_cols = [row[0] for row in result]

    if 'guided_state' not in existing_cols:
        conn.execute(text("ALTER TABLE conversations ADD COLUMN guided_state VARCHAR(50) DEFAULT 'idle'"))
        print("Added guided_state column")
    else:
        print("guided_state already exists")

    if 'pending_task_json' not in existing_cols:
        conn.execute(text("ALTER TABLE conversations ADD COLUMN pending_task_json TEXT"))
        print("Added pending_task_json column")
    else:
        print("pending_task_json already exists")

    conn.commit()
    print("Migration complete!")
