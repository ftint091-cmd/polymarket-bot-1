import logging
from app.observability.status_model import SystemStatus
from app.shared.time_utils import utcnow_iso

logger = logging.getLogger(__name__)

class StatusService:
    def __init__(self):
        self._last_status: SystemStatus | None = None

    def update(self, status: SystemStatus) -> None:
        self._last_status = status
        logger.debug("Status updated: cycle=%s state=%s", status.cycle_id, status.lifecycle_state)

    def get(self) -> SystemStatus | None:
        return self._last_status
