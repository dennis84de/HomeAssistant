"""AVM Fritz!Box connectivitiy sensor"""
import logging
from collections import defaultdict
from datetime import timedelta

from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType

from . import DATA_FRITZ_TOOLS_INSTANCE, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    _LOGGER.debug("Setting up sensors")
    fritzbox_tools = hass.data[DOMAIN][DATA_FRITZ_TOOLS_INSTANCE]

    async_add_entities([FritzBoxCallSensor(fritzbox_tools)], True)
    return True


class FritzBoxCallSensor(RestoreEntity):
    name = "FRITZ!Box Call list"
    entity_id = ENTITY_ID_FORMAT.format("fritzbox_call_list")
    icon = "mdi:phone"

    def __init__(self, fritzbox_tools):
        self.fritzbox_tools = fritzbox_tools
        self._state = 0
        self._is_available = (
            True  # set to False if an error happend during toggling the switch
        )
        self._attributes = defaultdict(str)
        super().__init__()

    @property
    def state(self):       
        return self._state

    @property
    def unique_id(self):
        return f"{self.fritzbox_tools.unique_id}-{self.entity_id}"

    @property
    def available(self) -> bool:
        return self._is_available

    @property
    def device_state_attributes(self) -> dict:
        return self._attributes

    async def _async_fetch_update(self):
        self._state = 0
        try:
            status = self.fritzbox_tools.fritzstatus
            callListResult = self.fritzbox_tools.fritzcalllist
            callDict = []
            
            for call in callListResult:                                                
                callType = None

                if (call.Type == "1"):
                  callType = "incoming"
                elif (call.Type == "2"):
                  callType = "missed"
                elif (call.Type == "3"):
                  callType = "outgoing"

                durationTimedelta = getattr(call, 'duration')

                callElement = {                    
                    'name': call.Name,                    
                    'number': call.CallerNumber if call.Type == "3" else call.Caller,
                    'date': getattr(call, 'date'),
                    'duration': durationTimedelta.seconds,
                    'calltype': callType
                }

                callDict.append(callElement)

            self._state = len(callListResult)
            self._is_available = True

            attr = dict()
            attr['calls'] = callDict
            attr['count'] = len(callListResult)

            self._attributes = attr

        except Exception:
            _LOGGER.error("Error getting the call list from the FRITZ!Box", exc_info=True)
            self._is_available = False

    async def async_update(self) -> None:
        _LOGGER.debug("Updating call list sensor...")
        await self._async_fetch_update()
