from .base_grader import BaseGrader
from environment.models import SystemState, ServiceStatus

class Task1Grader(BaseGrader):
    def grade(self, state: SystemState) -> float:
        score = 0.0
        
        # 1. Resolution (40%)
        if state.resolved:
            score += 0.4
        
        # 2. Correct Fix (30%)
        db = state.services.get("database")
        if db and db.config.get("db_memory_limit") == "2048mb" and db.status == ServiceStatus.running:
            score += 0.3
        
        # 3. Efficiency (30%)
        efficiency = max(0.0, (15 - state.step_count) / 15)
        score += 0.3 * efficiency

        # Penalties
        cascades = len([a for a in state.history if a.type == "restart_service" and a.target not in state.diagnosed_services])
        score -= cascades * 0.2

        return score
