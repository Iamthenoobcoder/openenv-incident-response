import os
import sys

# Add root project dir to path so environment and graders modules resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    from pydantic import BaseModel
    from environment.env import IncidentResponseEnv
    from environment.models import Action, Observation, SystemState, StepResponse
    from graders.grader_task1 import Task1Grader
    from graders.grader_task2 import Task2Grader
    from graders.grader_task3 import Task3Grader
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

try:
    app = FastAPI(title="Incident Response AI")
except Exception as e:
    print(f"Failed to initialize FastAPI: {e}")
    sys.exit(1)

from pydantic import BaseModel
from typing import Dict, Any

class AgentRequest(BaseModel):
    observation: Dict[str, Any]

# Simulation State Store (In-memory for demo)
current_env: IncidentResponseEnv = None

@app.get("/api/health")
def health():
    try:
        return {"status": "ok"}
    except Exception as e:
        print(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks")
def tasks():
    try:
        # Action schema fields required for an action in a step
        action_schema = {
            "type": "string (one of the action types)",
            "target": "string (service name or null)",
            "params": "object (optional parameters for edit_config or rollback)"
        }
        return {
            "tasks": [
                {"id": "task1_easy", "name": "Payment API Outage", "difficulty": "easy"},
                {"id": "task2_medium", "name": "Memory Leak + Red Herring", "difficulty": "medium"},
                {"id": "task3_hard", "name": "Bad Deployment + Angry Customers", "difficulty": "hard"}
            ],
            "action_schema": action_schema
        }
    except Exception as e:
        print(f"Failed to fetch tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ResetRequest(BaseModel):
    task_id: str
    seed: int = 42

@app.post("/api/reset", response_model=Observation)
def reset(req: ResetRequest):
    global current_env
    try:
        current_env = IncidentResponseEnv(req.task_id, req.seed)
        return current_env.reset()
    except Exception as e:
        print(f"Failed to reset environment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/step", response_model=StepResponse)
def step(action: Action):
    global current_env
    try:
        if not current_env:
            raise HTTPException(status_code=400, detail="No active session. Call /reset first.")
        return current_env.step(action)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Step failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/state", response_model=SystemState)
def state():
    global current_env
    try:
        if not current_env:
            raise HTTPException(status_code=404, detail="No active session")
        return current_env.get_state()
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to get state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/score")
def score():
    global current_env
    try:
        if not current_env:
            raise HTTPException(status_code=404, detail="No active session")
        return {"score": current_env.get_state().score}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to get score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/grader")
def grader():
    global current_env
    try:
        if not current_env:
            raise HTTPException(status_code=404, detail="No active session")
        
        state = current_env.get_state()
        if state.step_count == 0:
             return {"score": 0.0, "message": "Episode not started"}
        
        # Select grader based on task
        if current_env.task_id == "task1_easy":
            g = Task1Grader()
        elif current_env.task_id == "task2_medium":
            g = Task2Grader()
        elif current_env.task_id == "task3_hard":
            g = Task3Grader()
        else:
            return {"score": 0.0, "message": "Unknown task"}
            
        score = g.safe_grade(state)
        return {"score": score, "task_id": current_env.task_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Grader failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/baseline")
def run_baseline():
    return {
        'message': 'Run inference.py to generate real baseline scores.',
        'command': 'python inference.py',
        'results_file': 'baseline/results.json',
        'note': 'Scores depend on MODEL_NAME and HF_TOKEN env vars.'
    }

@app.get("/tasks")
def tasks_root():
    return tasks()

@app.get("/grader")
def grader_root():
    return grader()

@app.post("/api/agent")
def run_agent_api(req: AgentRequest):
    try:
        from openai import OpenAI
        import json
        api_key = os.getenv("HF_TOKEN", os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY", "AIzaSyBXkSjxI2hEcwfD-NGGnLdFggoDsGiG-pE")))
        client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
        )
            
        prompt = f"""You are an SRE AI Agent. Your goal is to resolve the incident.
Current Observation: {json.dumps(req.observation)}
Available Actions: check_logs, check_metrics, check_config, restart_service, edit_config, rollback_deployment, reply_customer, mark_resolved.
Think step by step. Return ONLY a JSON action object like {{"type": "check_logs", "target": "database", "params": {{}}}}."""
        
        max_retries = 5
        response = None
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
                    messages=[{"role": "user", "content": prompt}]
                )
                break
            except Exception as e:
                import time
                print(f"API Error ({e}). Waiting 15s before retry {attempt+1}/{max_retries}...")
                time.sleep(15)
                    
        if not response:
            print("Failed to get LLM response after retries. Using fallback action.")
            return {"type": "check_logs", "target": "web_server", "params": {"lines": 10}}
        action_text = response.choices[0].message.content
        if "```json" in action_text:
            action_text = action_text.split("```json")[1].split("```")[0].strip()
        elif "```" in action_text:
            action_text = action_text.split("```")[1].strip()
            
        action = json.loads(action_text)
        return action
    except Exception as e:
        print(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/baseline")
def run_baseline_root():
    return run_baseline()

@app.get("/api/actions")
def actions():
    try:
        return [
            "check_logs", "check_metrics", "check_connections",
            "check_config", "check_dependencies",
            "restart_service", "scale_service", "edit_config", "rollback_deployment", "clear_cache",
            "reply_customer", "update_status_page", "escalate_incident", "alert_team",
            "mark_resolved"
        ]
    except Exception as e:
        print(f"Failed to fetch actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files from dist if it exists (for production/Hugging Face)
dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")
if os.path.exists(dist_path):
    try:
        app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
        
        @app.exception_handler(404)
        async def not_found(request, exc):
            if request.url.path.startswith("/api/"):
                return {"detail": "Not Found"}
            return FileResponse(os.path.join(dist_path, "index.html"))
    except Exception as e:
        print(f"Failed to mount static files: {e}")
else:
    @app.get("/")
    def read_root():
        return {
            "name": "OpenEnv Incident Response API",
            "status": "online",
            "message": "Backend API is running properly. The frontend UI was not built or found in the dist directory."
        }

def main():
    import uvicorn
    import sys
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting FastAPI server on http://0.0.0.0:{port}")
    try:
        uvicorn.run("server.app:app", host="0.0.0.0", port=port, log_level="debug")
    except Exception as e:
        print(f"Failed to start uvicorn: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
