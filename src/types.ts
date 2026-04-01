export enum ActionType {
    check_logs = "check_logs",
    check_metrics = "check_metrics",
    check_connections = "check_connections",
    check_config = "check_config",
    check_dependencies = "check_dependencies",
    restart_service = "restart_service",
    scale_service = "scale_service",
    edit_config = "edit_config",
    rollback_deployment = "rollback_deployment",
    clear_cache = "clear_cache",
    reply_customer = "reply_customer",
    update_status_page = "update_status_page",
    escalate_incident = "escalate_incident",
    alert_team = "alert_team",
    mark_resolved = "mark_resolved"
}

export interface Action {
    type: ActionType | string;
    target: string | null;
    params: Record<string, any>;
}

export type ServiceStatus = "running" | "stopped" | "degraded" | "crashing";

export interface ServiceState {
    name: string;
    health: number;
    cpu: number;
    memory: number;
    error_rate: number;
    connections: number;
    status: ServiceStatus;
    config: Record<string, any>;
    version: string;
}

export interface CustomerTicket {
    id: string;
    customer: string;
    message: string;
    status: string;
    urgency: number;
    timestamp: string;
}

export interface LogEntry {
    timestamp: string;
    service: string;
    level: string;
    message: string;
}

export interface Alert {
    id: string;
    severity: string;
    service: string;
    message: string;
    timestamp: string;
}

export interface Observation {
    step_count: number;
    max_steps: number;
    services: Record<string, ServiceState>;
    recent_logs: LogEntry[];
    active_alerts: Alert[];
    customer_tickets: CustomerTicket[];
    action_feedback: string;
    cascade_warning: boolean;
    done: boolean;
    score_so_far: number;
}

export interface TaskConfig {
    id: string;
    name: string;
    difficulty: string;
}
