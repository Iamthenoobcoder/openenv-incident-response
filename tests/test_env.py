import pytest
from environment.env import IncidentResponseEnv
from environment.models import Action, ActionType, ServiceStatus

def test_env_reset():
    env = IncidentResponseEnv("task1_easy", 42)
    obs = env.reset()
    assert obs.step_count == 0
    assert "database" in obs.services
    assert obs.services["database"].status == ServiceStatus.crashing

def test_env_step():
    env = IncidentResponseEnv("task1_easy", 42)
    env.reset()
    action = Action(type=ActionType.check_logs, target="database")
    obs = env.step(action)
    assert obs.step_count == 1
    assert "database" in env.state.diagnosed_services

def test_cascade():
    env = IncidentResponseEnv("task1_easy", 42)
    env.reset()
    # Restart without diagnosis
    action = Action(type=ActionType.restart_service, target="database")
    obs = env.step(action)
    assert obs.cascade_warning is True
    assert obs.score_so_far < 0

def test_reproducibility():
    env1 = IncidentResponseEnv("task1_easy", 42)
    env2 = IncidentResponseEnv("task1_easy", 42)
    
    action = Action(type=ActionType.check_logs, target="database")
    obs1 = env1.step(action)
    obs2 = env2.step(action)
    
    assert obs1.model_dump() == obs2.model_dump()
