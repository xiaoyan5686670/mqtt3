#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from core.database import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        result = db.execute(text("PRAGMA table_info(devices)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'relay_on_payload' in columns and 'relay_off_payload' in columns:
            print("Fields already exist, skipping migration")
            return
        
        print("Adding relay payload fields to devices...")
        
        if 'relay_on_payload' not in columns:
            db.execute(text("ALTER TABLE devices ADD COLUMN relay_on_payload TEXT"))
            print("Added relay_on_payload field")
        
        if 'relay_off_payload' not in columns:
            db.execute(text("ALTER TABLE devices ADD COLUMN relay_off_payload TEXT"))
            print("Added relay_off_payload field")
        
        db.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print("Migration failed: " + str(e))
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
