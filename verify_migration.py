from data_manager import DataManager
import json
import os

ANALYTICS_FILE = 'analytics.json'

def test_migration():
    # 1. Ensure file exists with OLD format
    old_data = {
        "total_attempted": 10,
        "total_correct": 8,
        "streak": 5
    }
    with open(ANALYTICS_FILE, 'w') as f:
        json.dump(old_data, f)
        
    print("Created mock old analytics.json")
    
    # 2. Run Migration
    data = DataManager.load_analytics(ANALYTICS_FILE)
    print("Loaded data:", data)
    
    # 3. Verify
    if "performance" in data and "Legacy" in data["performance"]:
        print("SUCCESS: Data structure migrated!")
        print(f"Legacy Correct: {data['performance']['Legacy']['correct']}")
        print(f"Legacy Total: {data['performance']['Legacy']['total']}")
    else:
        print("FAILURE: Data not migrated correctly.")

if __name__ == "__main__":
    test_migration()
