from datetime import datetime
from ..models import SystemState, ServiceState, ServiceStatus, CustomerTicket, Alert

initial_state = SystemState(
    step_count=0,
    max_steps=25,
    services={
        "auth_service": ServiceState(
            name="auth_service",
            health=0.0,
            cpu=0.0,
            memory=10.0,
            error_rate=100.0,
            connections=0,
            status=ServiceStatus.crashing,
            config={"JWT_SECRET": "WRONG_SECRET"},
            version="v1.2.2"
        ),
        "gateway": ServiceState(
            name="gateway",
            health=0.4,
            cpu=20.0,
            memory=30.0,
            error_rate=60.0,
            connections=200,
            status=ServiceStatus.degraded,
            config={},
            version="v1.0.0"
        )
    },
    customer_tickets=[
        CustomerTicket(
            id="t3",
            customer="VIP",
            message="Cannot login",
            status="open",
            urgency=1.0,
            timestamp="2024-11-15T14:00:00Z"
        ),
        CustomerTicket(
            id="t4",
            customer="User456",
            message="502 error",
            status="open",
            urgency=0.7,
            timestamp="2024-11-15T14:00:00Z"
        ),
        CustomerTicket(
            id="t5",
            customer="User789",
            message="Dashboard down",
            status="open",
            urgency=0.5,
            timestamp="2024-11-15T14:00:00Z"
        )
    ],
    active_alerts=[
        Alert(
            id="a3",
            severity="critical",
            service="auth_service",
            message="Auth down after deploy",
            timestamp="2024-11-15T14:00:00Z"
        )
    ]
)
