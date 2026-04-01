from .models import SystemState, Action

def compute_reward(prev: SystemState, curr: SystemState, action: Action, cascade: bool) -> float:
    reward = 0.0

    # 1. Action rewards
    if action.type.startswith("check_"):
        reward += 0.02
    if action.type in ["edit_config", "rollback_deployment"]:
        reward += 0.10
    if action.type == "restart_service":
        reward += 0.02
    if action.type == "reply_customer":
        reward += 0.05

    # 2. Health improvement
    prev_health = sum(s.health for s in prev.services.values())
    curr_health = sum(s.health for s in curr.services.values())
    reward += 0.30 * (curr_health - prev_health)

    # 3. Resolution
    if curr.resolved and not prev.resolved:
        reward += 0.30

    # 4. Penalties
    if cascade:
        reward -= 0.25
    
    if prev.history:
        last_action = prev.history[-1]
        if last_action.type == action.type and last_action.target == action.target:
            reward -= 0.05

    return reward
