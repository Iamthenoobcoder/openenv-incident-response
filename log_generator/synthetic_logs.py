from datetime import datetime
from typing import List
from environment.models import SystemState, LogEntry, LogLevel, ServiceStatus

class SyntheticLogGenerator:
    def __init__(self, seed: int):
        self.seed = seed

    def get_logs(self, state: SystemState) -> List[LogEntry]:
        logs: List[LogEntry] = []
        now = datetime.now()

        for name, s in state.services.items():
            if s.status == ServiceStatus.crashing:
                logs.append(LogEntry(
                    timestamp=now.isoformat(),
                    service=name,
                    level=LogLevel.CRITICAL,
                    message=f"Process terminated unexpectedly. Error code: 137 (OOM)"
                ))
            elif s.status == ServiceStatus.degraded:
                logs.append(LogEntry(
                    timestamp=now.isoformat(),
                    service=name,
                    level=LogLevel.ERROR,
                    message=f"High latency detected in upstream dependencies. Error rate: {s.error_rate}%"
                ))
            else:
                logs.append(LogEntry(
                    timestamp=now.isoformat(),
                    service=name,
                    level=LogLevel.INFO,
                    message=f"Service heartbeat normal. CPU: {s.cpu}%"
                ))

        return logs[-20:]
