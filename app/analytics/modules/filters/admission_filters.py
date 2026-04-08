from app.analytics.base_module import BaseAnalyticsModule
from app.analytics.output_schema import ModuleOutput
from app.state.state_schema import CycleState

class AdmissionFiltersModule(BaseAnalyticsModule):
    name = "admission_filters"

    def run(self, state: CycleState, config: dict) -> ModuleOutput:
        return ModuleOutput(module_name=self.name, success=True, data={"admitted": True})
