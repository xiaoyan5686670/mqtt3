#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from core.database import SessionLocal

def setup_api_key():
    """Setup EMQX API Key"""
    db = SessionLocal()
    try:
        # Get active MQTT config
        result = db.execute(text("SELECT id, name, server FROM mqtt_configs WHERE is_active = 1"))
        config = result.fetchone()
        
        if not config:
            print("Error: No active MQTT config found!")
            print("Please activate a MQTT config first in MQTT Config Management page")
            return
        
        config_id = config[0]
        config_name = config[1]
        server = config[2]
        
        print(f"Active MQTT Config: {config_name} ({server})")
        print("")
        
        # Update API Key
        api_key = "f3d064c3dacad617"
        api_secret = "ezGnurOe8d4GV2LJF4Ptw46wnavTqL9AenBZyIoePWwP"
        api_port = 18083
        
        db.execute(text(
            "UPDATE mqtt_configs SET api_port = :port, api_key = :key, api_secret = :secret WHERE id = :id"
        ), {"port": api_port, "key": api_key, "secret": api_secret, "id": config_id})
        
        db.commit()
        
        print("Success! EMQX API Key configured:")
        print(f"  API Port: {api_port}")
        print(f"  API Key: {api_key}")
        print(f"  Secret Key: {api_secret[:20]}...")
        print("")
        print("You can now use the device online/offline status feature!")
        
    except Exception as e:
        print("Setup failed: " + str(e))
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    setup_api_key()
