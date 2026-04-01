import importlib
from .models import SystemState, Action, Observation, ServiceStatus
from .state_machine import apply_action
from .reward import compute_reward
from log_generator.synthetic_logs import SyntheticLogGenerator

class IncidentResponseEnv:
    def __init__(self, task_id: str, seed: int = 42):
        self.task_id = task_id
        self.seed = seed
        self.reset()

    def reset(self) -> Observation:
        self.log_generator = SyntheticLogGenerator(self.seed)
        self.state = self.get_initial_state(self.task_id)
        return self.get_observation("Environment reset. Task: " + self.task_id)

    def step(self, action: Action) -> dict:
        if self.state.step_count >= self.state.max_steps or self.state.resolved:
            return {
                "observation": self.get_observation("Episode already finished."),
                "reward": 0.0,
                "done": True,
                "info": {}
            }

        prev_state = self.state.model_copy(deep=True)
        next_state, feedback, cascade_triggered = apply_action(self.state, action)
        
        self.state = next_state
        self.state.step_count += 1
        self.state.history.append(action)

        reward = compute_reward(prev_state, self.state, action, cascade_triggered)
        self.state.score += reward

        done = self.state.step_count >= self.state.max_steps or self.state.resolved
        
        return {
            "observation": self.get_observation(feedback, cascade_triggered, done),
            "reward": reward,
            "done": done,
            "info": {"cascade": cascade_triggered}
        }

    def get_observation(self, feedback: str, cascade: bool = False, done: bool = False) -> Observation:
        return Observation(
            step_count=self.state.step_count,
            max_steps=self.state.max_steps,
            services=self.state.services,
            recent_logs=self.log_generator.get_logs(self.state),
            active_alerts=self.state.active_alerts,
            customer_tickets=self.state.customer_tickets,
            action_feedback=feedback,
            cascade_warning=cascade,
            done=done,
            score_so_far=self.state.score
        )

    def get_initial_state(self, task_id: str) -> SystemState:
        try:
            module_name = f"environment.scenarios.{task_id}"
            module = importlib.import_module(module_name)
            return module.initial_state.model_copy(deep=True)
        except Exception:
            from .scenarios import task1_easy
            return task1_easy.initial_state.model_copy(deep=True)

    def get_state(self) -> SystemState:
        return self.state
