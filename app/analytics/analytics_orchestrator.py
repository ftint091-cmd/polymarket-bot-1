import logging
import dataclasses
from app.analytics.base_module import BaseAnalyticsModule
from app.analytics.output_schema import ModuleOutput, AnalyticsSignal
from app.state.state_schema import CycleState, AnalyticsOutput

logger = logging.getLogger(__name__)

class AnalyticsOrchestrator:
    def __init__(self, modules: list[BaseAnalyticsModule]):
        self._modules = modules

    def run(self, state: CycleState, config: dict) -> AnalyticsOutput:
        all_signals: list[dict] = []
        module_outputs: dict[str, dict] = {}

        for module in self._modules:
            if not module.enabled:
                continue
            try:
                output: ModuleOutput = module.run(state, config)
                module_outputs[module.name] = dataclasses.asdict(output)
                for sig in output.signals:
                    all_signals.append(dataclasses.asdict(sig))
                logger.debug("Module %s: %d signals", module.name, len(output.signals))
            except Exception as e:
                logger.error("Module %s failed: %s", module.name, e)
                module_outputs[module.name] = {"error": str(e), "success": False}

        return AnalyticsOutput(signals=all_signals, module_outputs=module_outputs)
