from .base_grader import BaseGrader
from environment.models import SystemState

class Task2Grader(BaseGrader):
    def grade(self, state: SystemState) -> float:
        score = 0.0
        if state.resolved:
            score += 0.5
        ws = state.services.get("web_server")
        if ws and ws.config.get("connection_timeout") == "30s":
            score += 0.3
        
        efficiency = max(0.0, (20 - state.step_count) / 20)
        score += 0.2 * efficiency
        
        return score
