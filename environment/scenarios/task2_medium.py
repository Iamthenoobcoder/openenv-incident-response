from datetime import datetime
from ..models import SystemState, ServiceState, ServiceStatus, CustomerTicket, Alert

initial_state = SystemState(
    step_count=0,
    max_steps=20,
    services={
        "web_server": ServiceState(
            name="web_server",
            health=0.5,
            cpu=40.0,
            memory=95.0,
            error_rate=15.0,
            connections=500,
            status=ServiceStatus.degraded,
            config={"connection_timeout": None},
            version="v2.0.1"
        ),
        "cache": ServiceState(
            name="cache",
            health=1.0,
            cpu=87.0,
            memory=30.0,
            error_rate=0.0,
            connections=1000,
            status=ServiceStatus.running,
            config={},
            version="v1.5.0"
        )
    },
    customer_tickets=[
        CustomerTicket(
            id="t2",
            customer="Shopify",
            message="Sluggish response",
            status="open",
            urgency=0.6,
            timestamp=datetime.now().isoformat()
        )
    ],
    active_alerts=[
        Alert(
            id="a2",
            severity="medium",
            service="web_server",
            message="High memory",
            timestamp=datetime.now().isoformat()
        )
    ]
)
