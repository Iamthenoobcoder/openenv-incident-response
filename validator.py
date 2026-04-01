import requests
import yaml
import os

def validate_openenv():
    print("Checking openenv.yaml...")
    if not os.path.exists("openenv.yaml"):
        print("!! openenv.yaml missing")
        return False
    
    with open("openenv.yaml", "r") as f:
        spec = yaml.safe_load(f)
        required = ["name", "version", "environment", "tasks", "actions"]
        for field in required:
            if field not in spec:
                print(f"!! Missing field in openenv.yaml: {field}")
                return False
    print("OK: openenv.yaml valid")
    return True

def validate_api():
    print("Checking API endpoints...")
    base_url = "http://localhost:7860/api"
    
    try:
        # Health
        res = requests.get(f"{base_url}/health")
        if res.status_code != 200:
            print(f"!! Health check failed: {res.status_code}")
            return False
            
        # Tasks
        res = requests.get(f"{base_url}/tasks")
        data = res.json()
        if "tasks" not in data or "action_schema" not in data:
            print("!! Tasks endpoint missing required fields")
            return False
            
        # Reset
        res = requests.post(f"{base_url}/reset", json={"task_id": "task1_easy"})
        if res.status_code != 200:
            print(f"!! Reset failed: {res.status_code}")
            return False
            
        # Step
        action = {"type": "check_logs", "target": "database", "params": {}}
        res = requests.post(f"{base_url}/step", json=action)
        data = res.json()
        required_step = ["observation", "reward", "done", "info"]
        for field in required_step:
            if field not in data:
                print(f"!! Step response missing field: {field}")
                return False
                
        # State
        res = requests.get(f"{base_url}/state")
        if res.status_code != 200:
            print("!! State endpoint failed")
            return False
            
        # Grader
        res = requests.get(f"{base_url}/grader")
        if "score" not in res.json():
            print("!! Grader endpoint failed")
            return False
            
    except Exception as e:
        print(f"!! API validation error: {e}")
        return False
        
    print("OK: API endpoints valid")
    return True

if __name__ == "__main__":
    v1 = validate_openenv()
    v2 = validate_api()
    if v1 and v2:
        print("--- ALL VALIDATIONS PASSED ---")
    else:
        print("--- VALIDATION FAILED ---")
