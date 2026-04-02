import os
import json
import time
import requests
from dotenv import load_dotenv
from openai import OpenAI
from baseline.system_prompt import SYSTEM_PROMPT
from baseline.parse_action import parse_action

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
API_KEY = os.getenv("HF_TOKEN", os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY")))
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")

client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL
)

BASE_URL = "http://localhost:7860/api"

def run_task(task_id: str):
    print(f"--- Running Task: {task_id} ---")
    
    # 1. Reset
    res = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id, "seed": 42})
    obs = res.json()
    
    history = []
    
    FALLBACK_ACTION = {
        'type': 'check_logs',
        'target': 'web_server',
        'params': {'lines': 10}
    }
    
    while not obs.get("done"):
        print(f"Step {obs['step_count']}: Score {obs['score_so_far']:.2f}")
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Current Observation: {json.dumps(obs)}\n\nWhat is your next action?"}
                    ]
                )
                break
            except Exception as e:
                import time
                print(f"Rate limit or other error: {e}. Waiting 15s...")
                time.sleep(15)
        else:
            print("Failed after max retries")
            break
            
        message_text = response.choices[0].message.content
        action = parse_action(message_text)
        if not action:
            print(f"!! Parse failed, using fallback")
            action = FALLBACK_ACTION
            
        print(f"> Action: {action.get('type')} on {action.get('target')}")
        
        # 3. Step
        res = requests.post(f"{BASE_URL}/step", json=action)
        obs = res.json()
        history.append({"action": action, "feedback": obs.get("action_feedback")})
        
        if obs.get("done"):
            break
            
    # Fetch final score using the programmatic grader
    grader_res = requests.get(f"{BASE_URL}/grader")
    final_score = grader_res.json().get("score", 0.0)
    
    print(f"--- Task Complete: {task_id} | Final Score: {final_score:.2f} ---")
    return final_score, history

def main():
    tasks = ["task1_easy", "task2_medium", "task3_hard"]
    results = {}
    
    for task in tasks:
        score, history = run_task(task)
        results[task] = {"score": score, "history": history}
        
    os.makedirs("baseline", exist_ok=True)
    with open("baseline/results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
