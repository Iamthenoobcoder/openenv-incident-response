from datetime import datetime
from ..models import SystemState, ServiceState, ServiceStatus, CustomerTicket, Alert

initial_state = SystemState(
    step_count=0,
    max_steps=15,
    services={
        "database": ServiceState(
            name="database",
            health=0.0,
            cpu=5.0,
            memory=100.0,
            error_rate=0.0,
            connections=0,
            status=ServiceStatus.crashing,
            config={"db_memory_limit": "512mb"},
            version="v1.0.0"
        ),
        "payment_api": ServiceState(
            name="payment_api",
            health=0.2,
            cpu=10.0,
            memory=20.0,
            error_rate=80.0,
            connections=50,
            status=ServiceStatus.degraded,
            config={},
            version="v1.1.0"
        )
    },
    customer_tickets=[
        CustomerTicket(
            id="t1",
            customer="User123",
            message="Payments failing",
            status="open",
            urgency=0.8,
            timestamp="2024-11-15T14:00:00Z"
        )
    ],
    active_alerts=[
        Alert(
            id="a1",
            severity="critical",
            service="database",
            message="OOM Killed",
            timestamp="2024-11-15T14:00:00Z"
        )
    ]
)
