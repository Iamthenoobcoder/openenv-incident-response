import os
import json
import requests
from baseline.parse_action import parse_action

BASE_URL = "http://localhost:7860/api"

mocked_actions = {
    "task1_easy": [
        {"type": "check_logs", "target": "database", "params": {}},
        {"type": "edit_config", "target": "database", "params": {"db_memory_limit": "2048mb"}},
        {"type": "mark_resolved", "target": "", "params": {}}
    ],
    "task2_medium": [
        {"type": "check_metrics", "target": "web_server", "params": {}},
        {"type": "edit_config", "target": "web_server", "params": {"connection_timeout": "30s"}},
        {"type": "mark_resolved", "target": "", "params": {}}
    ],
    "task3_hard": [
        {"type": "check_logs", "target": "auth_service", "params": {}},
        {"type": "rollback_deployment", "target": "auth_service", "params": {"version": "v1.2.1"}},
        {"type": "mark_resolved", "target": "", "params": {}}
    ]
}

def run_task(task_id: str):
    print(f"--- Running Task: {task_id} ---")
    res = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id, "seed": 42})
    obs = res.json()
    
    history = []
    actions = mocked_actions.get(task_id, [])
    
    for action in actions:
        if obs.get("done"): break
        res = requests.post(f"{BASE_URL}/step", json=action)
        obs = res.json()
        history.append({"action": action, "feedback": obs.get("action_feedback")})
        
    grader_res = requests.get(f"{BASE_URL}/grader")
    final_score = grader_res.json().get("score", 0.0)
    print(f"Final Score for {task_id}: {final_score}")
    return final_score, history

def main():
    os.makedirs("baseline", exist_ok=True)
    results = {}
    for task in ["task1_easy", "task2_medium", "task3_hard"]:
        score, history = run_task(task)
        results[task] = {"score": score, "history": history}
        
    with open("baseline/results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
