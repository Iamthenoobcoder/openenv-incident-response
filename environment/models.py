from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    check_logs = "check_logs"
    check_metrics = "check_metrics"
    check_connections = "check_connections"
    check_config = "check_config"
    check_dependencies = "check_dependencies"
    restart_service = "restart_service"
    scale_service = "scale_service"
    edit_config = "edit_config"
    rollback_deployment = "rollback_deployment"
    clear_cache = "clear_cache"
    reply_customer = "reply_customer"
    update_status_page = "update_status_page"
    escalate_incident = "escalate_incident"
    alert_team = "alert_team"
    mark_resolved = "mark_resolved"

class Action(BaseModel):
    type: ActionType
    target: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class ServiceStatus(str, Enum):
    running = "running"
    stopped = "stopped"
    degraded = "degraded"
    crashing = "crashing"

class ServiceState(BaseModel):
    name: str
    health: float
    cpu: float
    memory: float
    error_rate: float
    connections: int
    status: ServiceStatus
    config: Dict[str, Any] = Field(default_factory=dict)
    version: str

class CustomerTicket(BaseModel):
    id: str
    customer: str
    message: str
    status: str  # "open" or "resolved"
    urgency: float
    timestamp: str

class LogLevel(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogEntry(BaseModel):
    timestamp: str
    service: str
    level: LogLevel
    message: str

class Alert(BaseModel):
    id: str
    severity: str
    service: str
    message: str
    timestamp: str

class SystemState(BaseModel):
    step_count: int
    max_steps: int
    services: Dict[str, ServiceState]
    customer_tickets: List[CustomerTicket]
    active_alerts: List[Alert]
    history: List[Action] = Field(default_factory=list)
    diagnosed_services: List[str] = Field(default_factory=list)
    resolved: bool = False
    score: float = 0.0

class Observation(BaseModel):
    step_count: int
    max_steps: int
    services: Dict[str, ServiceState]
    recent_logs: List[LogEntry]
    active_alerts: List[Alert]
    customer_tickets: List[CustomerTicket]
    action_feedback: str
    cascade_warning: bool
    done: bool
    score_so_far: float

class Reward(BaseModel):
    value: float
    components: Dict[str, float]

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]
