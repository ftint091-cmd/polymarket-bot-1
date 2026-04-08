from abc import ABC, abstractmethod
from app.state.state_schema import CycleState
from app.analytics.output_schema import ModuleOutput

class BaseAnalyticsModule(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    def enabled(self) -> bool:
        return True

    @abstractmethod
    def run(self, state: CycleState, config: dict) -> ModuleOutput:
        ...
