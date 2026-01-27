import sys
import os
import json
import asyncio

# Use the absolute path to mqtt4/backend
BACKEND_PATH = "/Users/qinxiaoyan/mqtt4/backend"
sys.path.append(BACKEND_PATH)

print("--- Testing Backend Modules ---")

try:
    import schemas
    import models
    import database
    import engine
    print("✓ All modules imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 1: Database Initialization
print("\n--- Testing Database ---")
try:
    from database import engine as db_engine
    from models import Base, Flow
    Base.metadata.create_all(bind=db_engine)
    print("✓ Tables created successfully")
except Exception as e:
    print(f"✗ DB Init failed: {e}")

# Test 2: Schema Validation
print("\n--- Testing Schema Validation ---")
test_graph = {
    "nodes": [
        {
            "id": "node-1",
            "type": "input",
            "data": {"label": "Test Source", "broker": "localhost", "topic": "test"},
            "position": {"x": 10, "y": 10}
        }
    ],
    "edges": []
}
try:
    graph_obj = schemas.FlowGraph(**test_graph)
    print("✓ Schema validation passed")
except Exception as e:
    print(f"✗ Schema validation failed: {e}")

# Test 3: Engine Logic (Stateless parts)
print("\n--- Testing Engine Logic ---")
try:
    from engine import engine as flow_engine
    print(f"✓ Engine instance created (running={flow_engine.running})")
except Exception as e:
    print(f"✗ Engine test failed: {e}")

print("\n--- Verification Finished ---")
