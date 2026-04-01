import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from baseline.system_prompt import SYSTEM_PROMPT
from baseline.parse_action import parse_action

load_dotenv()

# The judges will inject these, but we fallback gracefully for local testing!
API_BASE_URL = os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
API_KEY = os.getenv("HF_TOKEN", os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY")))
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

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
    
    while not obs.get("done"):
        print(f"Step {obs['step_count']}: Score {obs['score_so_far']:.2f}")
        
        # 2. Get AI Action using standardized OpenAI layout
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Current Observation: {json.dumps(obs)}\n\nWhat is your next action?"}
            ]
        )
        
        message_text = response.choices[0].message.content
        action = parse_action(message_text)
        if not action:
            print(f"!! Failed to parse action from: {message_text}")
            break
            
        print(f"> Action: {action.get('type')} on {action.get('target')}")
        
        # 3. Step
        res = requests.post(f"{BASE_URL}/step", json=action)
        obs = res.json()
        history.append({"action": action, "feedback": obs.get("action_feedback")})
        
        if obs.get("done"):
            break
            
    print(f"--- Task Complete: {task_id} | Final Score: {obs.get('score_so_far', 0):.2f} ---")
    return obs.get('score_so_far', 0), history

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
