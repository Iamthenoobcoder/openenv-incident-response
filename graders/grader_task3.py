from .base_grader import BaseGrader
from environment.models import SystemState

class Task3Grader(BaseGrader):
    def grade(self, state: SystemState) -> float:
        score = 0.0
        if state.resolved:
            score += 0.5
        auth = state.services.get("auth_service")
        if auth and auth.version == "v1.2.1":
            score += 0.3
        
        tickets_resolved = len([t for t in state.customer_tickets if t.status == "resolved"])
        score += (tickets_resolved / 3) * 0.2
        
        return score
