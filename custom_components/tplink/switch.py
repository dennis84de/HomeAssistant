"""Support for TPLink HS100/HS110/HS200 smart switch."""
import asyncio
import logging
import time

from pyHS100 import SmartDeviceException, SmartPlug

from homeassistant.components.switch import (
    ATTR_CURRENT_POWER_W,
    ATTR_TODAY_ENERGY_KWH,
    SwitchEntity,
)
from homeassistant.const import ATTR_VOLTAGE
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.typing import HomeAssistantType

from . import CONF_SWITCH, DOMAIN as TPLINK_DOMAIN

PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)

ATTR_TOTAL_ENERGY_KWH = "total_energy_kwh"
ATTR_CURRENT_A = "current_a"

MAX_ATTEMPTS = 20
SLEEP_TIME = 1


async def async_setup_entry(hass: HomeAssistantType, config_entry, async_add_entities):
    """Set up switches."""
    for device in hass.data[TPLINK_DOMAIN][CONF_SWITCH]:
        await hass.async_add_executor_job(device.get_sysinfo)
        async_add_entities([SmartPlugSwitch(device)], update_before_add=True)
    return True


class SmartPlugSwitch(SwitchEntity):
    """Representation of a TPLink Smart Plug switch."""

    def __init__(self, smartplug: SmartPlug):
        """Initialize the switch."""
        self.smartplug = smartplug
        self._sysinfo = None
        self._state = None
        self._is_available = False
        # Set up emeter cache
        self._emeter_params = {}

        self._mac = None
        self._alias = None
        self._host = None
        self._model = None
        self._device_id = None

        self._is_ready = False

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._device_id

    @property
    def name(self):
        """Return the name of the Smart Plug."""
        return self._alias

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "name": self._alias,
            "model": self._model,
            "manufacturer": "TP-Link",
            "connections": {(dr.CONNECTION_NETWORK_MAC, self._mac)},
            "sw_version": self._sysinfo["sw_ver"],
        }

    @property
    def available(self) -> bool:
        """Return if switch is available."""
        return self._is_available

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self.smartplug.turn_on()

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self.smartplug.turn_off()
        self.update_state()

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._emeter_params

    @property
    def _plug_from_context(self):
        """Return the plug from the context."""
        children = self.smartplug.sys_info["children"]
        return next(c for c in children if c["id"] == self.smartplug.context)

    def update_state(self):
        """Update the TP-Link switch's state."""
        if self.smartplug.context is None:
            self._state = self.smartplug.state == self.smartplug.SWITCH_STATE_ON
        else:
            self._state = self._plug_from_context["state"] == 1

    def attempt_update(self, update_attempt):
        """Attempt to get details from the TP-Link switch."""
        try:
            if not self._sysinfo:
                self._sysinfo = self.smartplug.sys_info
                self._host = self.smartplug.host
                self._mac = self.smartplug.mac
                self._model = self.smartplug.model
                if self.smartplug.context is None:
                    self._alias = self.smartplug.alias
                    self._device_id = self._mac
                else:
                    self._alias = self._plug_from_context["alias"]
                    self._device_id = self.smartplug.context

            self.update_state()

            if self.smartplug.has_emeter:
                emeter_readings = self.smartplug.get_emeter_realtime()

                self._emeter_params[ATTR_CURRENT_POWER_W] = "{:.2f}".format(
                    emeter_readings["power"]
                )
                self._emeter_params[ATTR_TOTAL_ENERGY_KWH] = "{:.3f}".format(
                    emeter_readings["total"]
                )
                self._emeter_params[ATTR_VOLTAGE] = "{:.1f}".format(
                    emeter_readings["voltage"]
                )
                self._emeter_params[ATTR_CURRENT_A] = "{:.2f}".format(
                    emeter_readings["current"]
                )

                emeter_statics = self.smartplug.get_emeter_daily()
                try:
                    self._emeter_params[ATTR_TODAY_ENERGY_KWH] = "{:.3f}".format(
                        emeter_statics[int(time.strftime("%e"))]
                    )
                except KeyError:
                    # Device returned no daily history
                    pass
            self._is_ready = True
        except (SmartDeviceException, OSError) as ex:
            _LOGGER.warning(
                "Attempt %s - retrying in %s for %s|%s due to: %s",
                update_attempt,
                SLEEP_TIME,
                self._host,
                self._alias,
                ex,
            )

    async def async_update(self):
        """Update the TP-Link switch's state."""
        for update_attempt in range(MAX_ATTEMPTS):
            self._is_ready = False

            await self.hass.async_add_executor_job(self.attempt_update, update_attempt)

            if self._is_ready:
                self._is_available = True
                break

            await asyncio.sleep(SLEEP_TIME)

        else:
            if self._is_available:
                _LOGGER.warning(
                    "Could not read state for %s|%s", self._host, self._alias
                )
            self._is_available = False
