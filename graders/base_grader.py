from abc import ABC, abstractmethod
from environment.models import SystemState

class BaseGrader(ABC):
    @abstractmethod
    def grade(self, state: SystemState) -> float:
        pass

    def safe_grade(self, state: SystemState) -> float:
        try:
            score = self.grade(state)
            return max(0.0, min(1.0, score))
        except Exception as e:
            print(f"Grader error: {e}")
            return 0.0
