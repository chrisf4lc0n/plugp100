import logging
from typing import Optional, Any

from plugp100.api.requests.tapo_request import TapoRequest
from plugp100.api.tapo_client import TapoClient
from plugp100.new.components.device_component import DeviceComponent
from plugp100.responses.energy_info import EnergyInfo
from plugp100.responses.power_info import PowerInfo

_LOGGER = logging.getLogger(__name__)


class EnergyComponent(DeviceComponent):
    def __init__(self, client: TapoClient, child_id: str | None = None):
        self._client = client
        self._energy_usage = None
        self._power_info = None
        self._child_id = child_id

    async def update(self, current_state: dict[str, Any] | None = None):
        try:
            if self._child_id:
                # For child devices (e.g., power strip sockets), use control_child
                energy_request = TapoRequest.get_energy_usage()
                power_request = TapoRequest.get_current_power()
                energy_usage = await self._client.control_child(self._child_id, energy_request)
                power_info = await self._client.control_child(self._child_id, power_request)
                self._energy_usage = EnergyInfo(energy_usage.value) if energy_usage.is_success() else None
                self._power_info = PowerInfo(power_info.value) if power_info.is_success() else None
            else:
                energy_usage = await self._client.get_energy_usage()
                power_info = await self._client.get_current_power()
                self._energy_usage = energy_usage.value if energy_usage.is_success() else None
                self._power_info = power_info.value if power_info.is_success() else None
        except Exception as e:
            _LOGGER.debug("Failed to update energy component for child %s: %s", self._child_id, e)
            # Don't re-raise - allow the device to continue working even if energy monitoring fails
            self._energy_usage = None
            self._power_info = None

    @property
    def energy_info(self) -> Optional[EnergyInfo]:
        return self._energy_usage

    @property
    def power_info(self) -> Optional[PowerInfo]:
        return self._power_info
