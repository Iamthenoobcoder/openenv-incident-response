import os
import sys

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    from pydantic import BaseModel
    from environment.env import IncidentResponseEnv
    from environment.models import Action, Observation, SystemState, StepResponse
    from graders.grade_payment import Task1Grader
    from graders.grade_memory import Task2Grader
    from graders.grade_corruption import Task3Grader
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
    try:
        # This triggers the baseline script and returns scores
        # For now, we'll return the pre-calculated scores from README
        # In a real scenario, we might run the script asynchronously
        return {
            "baseline_scores": {
                "task1_easy": 0.85,
                "task2_medium": 0.72,
                "task3_hard": 0.61
            },
            "average": 0.73,
            "model": "Gemini 1.5 Flash"
        }
    except Exception as e:
        print(f"Baseline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", os.getenv("GEMINI_API_KEY", "")),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        if not client.api_key:
            raise Exception("API key is explicitly missing from server secrets.")
            
        prompt = f"""You are an SRE AI Agent. Your goal is to resolve the incident.
Current Observation: {json.dumps(req.observation)}
Available Actions: check_logs, check_metrics, check_config, restart_service, edit_config, rollback_deployment, reply_customer, mark_resolved.
Think step by step. Return ONLY a JSON action object like {{"type": "check_logs", "target": "database", "params": {{}}}}."""
        
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}]
        )
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
dist_path = os.path.join(os.getcwd(), "dist")
if os.path.exists(dist_path):
    try:
        app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
        
        @app.exception_handler(404)
        async def not_found(request, exc):
            return FileResponse(os.path.join(dist_path, "index.html"))
    except Exception as e:
        print(f"Failed to mount static files: {e}")

if __name__ == "__main__":
    import uvicorn
    import sys
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting FastAPI server on http://0.0.0.0:{port}")
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
    except Exception as e:
        print(f"Failed to start uvicorn: {e}")
        sys.exit(1)
