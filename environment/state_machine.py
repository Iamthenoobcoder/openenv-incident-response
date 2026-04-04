from .models import SystemState, Action, ServiceStatus

def apply_action(state: SystemState, action: Action) -> tuple[SystemState, str, bool]:
    next_state = state.model_copy(deep=True)
    feedback = ""
    cascade_triggered = False

    target_service = next_state.services.get(action.target) if action.target else None

    if action.type == "check_logs":
        feedback = f"Inspecting logs for {action.target or 'system'}... Found recent anomalies."
        if action.target and action.target not in next_state.diagnosed_services:
            next_state.diagnosed_services.append(action.target)

    elif action.type == "check_metrics":
        if target_service:
            feedback = f"Metrics for {action.target}: CPU {target_service.cpu}%, MEM {target_service.memory}%, Errors {target_service.error_rate}%"
            if action.target not in next_state.diagnosed_services:
                next_state.diagnosed_services.append(action.target)
        else:
            feedback = "System-wide metrics look unstable."

    elif action.type == "check_config":
        if target_service:
            feedback = f"Current config for {action.target}: {target_service.config}"
            if action.target not in next_state.diagnosed_services:
                next_state.diagnosed_services.append(action.target)
        else:
            feedback = "Global configuration is locked."

    elif action.type == "restart_service":
        if target_service:
            if action.target not in state.diagnosed_services:
                cascade_triggered = True
                feedback = f"CRITICAL: Restarted {action.target} without diagnosis. Cascading failure triggered!"
                trigger_cascade(next_state, action.target)
            else:
                feedback = f"Restarting {action.target}... Service is coming back online."
                target_service.status = ServiceStatus.running
                target_service.health = min(1.0, target_service.health + 0.2)

    elif action.type == "edit_config":
        if target_service and action.params:
            target_service.config.update(action.params)
            feedback = f"Updated configuration for {action.target}."
            check_resolution(next_state, action)

    elif action.type == "rollback_deployment":
        if target_service and action.params.get("version"):
            target_service.version = action.params["version"]
            feedback = f"Rolling back {action.target} to {target_service.version}..."
            check_resolution(next_state, action)

    elif action.type == "reply_customer":
        open_ticket = next(
            (t for t in next_state.customer_tickets if t.status == "open"), None
        )
        if open_ticket:
            open_ticket.status = "resolved"
            feedback = f"Replied to customer {open_ticket.customer}. Ticket resolved."
        else:
            feedback = "No open customer tickets found."

    elif action.type == "mark_resolved":
        next_state.resolved = True
        feedback = "Incident marked as resolved by agent."

    else:
        feedback = f"Action {action.type} executed."

    return next_state, feedback, cascade_triggered

def trigger_cascade(state: SystemState, source: str):
    for name, s in state.services.items():
        if name != source:
            s.health = max(0, s.health - 0.3)
            s.error_rate = min(100, s.error_rate + 20)
            s.status = ServiceStatus.degraded

def check_resolution(state: SystemState, action: Action):
    # Task 1: Database OOM
    if (
        action.type == "edit_config"
        and action.target == "database"
        and action.params.get("db_memory_limit") == "2048mb"
    ):
        state.services["database"].health = 1.0
        state.services["database"].status = ServiceStatus.running
        state.services["database"].error_rate = 0
        if "payment_api" in state.services:
            state.services["payment_api"].health = 1.0
            state.services["payment_api"].status = ServiceStatus.running
            state.services["payment_api"].error_rate = 0

    # Task 3: Bad JWT
    if (
        action.type == "rollback_deployment"
        and action.target == "auth_service"
        and action.params.get("version") == "v1.2.1"
    ):
        state.services["auth_service"].health = 1.0
        state.services["auth_service"].status = ServiceStatus.running
        state.services["auth_service"].error_rate = 0
