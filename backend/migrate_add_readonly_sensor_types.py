#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from core.database import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        result = db.execute(text("PRAGMA table_info(topic_configs)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'readonly_sensor_types' in columns:
            print("Field already exists, skipping migration")
            return
        
        print("Adding readonly_sensor_types field to topic_configs...")
        
        db.execute(text("ALTER TABLE topic_configs ADD COLUMN readonly_sensor_types TEXT"))
        print("Added readonly_sensor_types field")
        
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
