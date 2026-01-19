#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from core.database import SessionLocal

def migrate():
    db = SessionLocal()
    try:
        result = db.execute(text("PRAGMA table_info(mqtt_configs)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'api_port' in columns and 'api_key' in columns and 'api_secret' in columns:
            print("Fields already exist, skipping migration")
            return
        
        print("Adding EMQX API fields...")
        
        if 'api_port' not in columns:
            db.execute(text("ALTER TABLE mqtt_configs ADD COLUMN api_port INTEGER DEFAULT 18083"))
            print("Added api_port field")
        
        if 'api_key' not in columns:
            db.execute(text("ALTER TABLE mqtt_configs ADD COLUMN api_key TEXT"))
            print("Added api_key field")
        
        if 'api_secret' not in columns:
            db.execute(text("ALTER TABLE mqtt_configs ADD COLUMN api_secret TEXT"))
            print("Added api_secret field")
        
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
