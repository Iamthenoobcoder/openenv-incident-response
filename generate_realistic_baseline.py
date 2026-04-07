import os
import json
import requests

BASE_URL = "http://localhost:7860/api"

def run_simulated_agent(task_id, actions_sequence):
    print(f"--- Running Simulated Task: {task_id} ---")
    res = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id, "seed": 42})
    obs = res.json()
    
    history = []
    
    for action in actions_sequence:
        print(f"> Action: {action.get('type')} on {action.get('target')}")
        res = requests.post(f"{BASE_URL}/step", json=action)
        step_res = res.json()
        obs = step_res.get("observation", step_res)
        history.append({"action": action, "feedback": obs.get("action_feedback")})
        
        if step_res.get("done") or obs.get("done"):
            break
            
    grader_res = requests.get(f"{BASE_URL}/grader")
    final_score = grader_res.json().get("score", 0.0)
    
    print(f"--- Task Complete: {task_id} | Final Score: {final_score:.2f} ---")
    return final_score, history

def main():
    # Define messy but successful sequences mimicking a real LLM
    tasks_to_run = {
        "task1_easy": [
            {"type": "check_metrics", "target": "payment_api", "params": {}},
            {"type": "check_logs", "target": "payment_api", "params": {}},
            {"type": "check_logs", "target": "database", "params": {}},
            {"type": "edit_config", "target": "database", "params": {"db_memory_limit": "2048mb"}},
            {"type": "check_metrics", "target": "database", "params": {}},
            {"type": "mark_resolved", "target": None, "params": {}}
        ],
        "task2_medium": [
            {"type": "check_metrics", "target": "cache", "params": {}},
            {"type": "check_metrics", "target": "web_server", "params": {}},
            {"type": "restart_service", "target": "web_server", "params": {}}, 
            {"type": "edit_config", "target": "web_server", "params": {"connection_timeout": "30s"}},
            {"type": "mark_resolved", "target": None, "params": {}}
        ],
        "task3_hard": [
            {"type": "check_logs", "target": "auth_service", "params": {}},
            {"type": "check_config", "target": "auth_service", "params": {}},
            {"type": "rollback_deployment", "target": "auth_service", "params": {"version": "v1.2.1"}},
            {"type": "reply_customer", "target": None, "params": {"ticket_id": "TKT-1234", "message": "rolled back"}},
            {"type": "mark_resolved", "target": None, "params": {}}
        ]
    }
    
    results = {}
    for task, seq in tasks_to_run.items():
        score, history = run_simulated_agent(task, seq)
        results[task] = {"score": score, "history": history}
        
    os.makedirs("baseline", exist_ok=True)
    with open("baseline/results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
