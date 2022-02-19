"""Services for Fritz integration."""
import logging

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.service import async_extract_config_entry_ids

from .common import AvmWrapper
from .const import (
    DOMAIN,
    FRITZ_SERVICES,
    SERVICE_CLEANUP,
    SERVICE_REBOOT,
    SERVICE_RECONNECT,
)

_LOGGER = logging.getLogger(__name__)


SERVICE_LIST = [SERVICE_CLEANUP, SERVICE_REBOOT, SERVICE_RECONNECT]


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Fritz integration."""

    for service in SERVICE_LIST:
        if hass.services.has_service(DOMAIN, service):
            return

    async def async_call_fritz_service(service_call: ServiceCall) -> None:
        """Call correct Fritz service."""

        if not (
            fritzbox_entry_ids := await _async_get_configured_avm_device(
                hass, service_call
            )
        ):
            raise HomeAssistantError(
                f"Failed to call service '{service_call.service}'. Config entry for target not found"
            )

        for entry_id in fritzbox_entry_ids:
            _LOGGER.debug("Executing service %s", service_call.service)
            avm_wrapper: AvmWrapper = hass.data[DOMAIN][entry_id]
            if config_entry := hass.config_entries.async_get_entry(entry_id):
                await avm_wrapper.service_fritzbox(service_call, config_entry)
            else:
                _LOGGER.error(
                    "Executing service %s failed, no config entry found",
                    service_call.service,
                )

    for service in SERVICE_LIST:
        hass.services.async_register(DOMAIN, service, async_call_fritz_service)


async def _async_get_configured_avm_device(
    hass: HomeAssistant, service_call: ServiceCall
) -> list:
    """Get FritzBoxTools class from config entry."""

    list_entry_id: list = []
    for entry_id in await async_extract_config_entry_ids(hass, service_call):
        config_entry = hass.config_entries.async_get_entry(entry_id)
        if (
            config_entry
            and config_entry.domain == DOMAIN
            and config_entry.state == ConfigEntryState.LOADED
        ):
            list_entry_id.append(entry_id)
    return list_entry_id


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for Fritz integration."""

    if not hass.data.get(FRITZ_SERVICES):
        return

    hass.data[FRITZ_SERVICES] = False

    for service in SERVICE_LIST:
        hass.services.async_remove(DOMAIN, service)
