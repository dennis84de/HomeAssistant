"""
Support for switch devices that can be controlled using the RaspyRFM rc module.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.brematic/
"""
import asyncio
import logging

import voluptuous as vol

from homeassistant.components.switch import (
    DOMAIN, PLATFORM_SCHEMA, SwitchDevice, ENTITY_ID_FORMAT)
from homeassistant.const import (
    ATTR_FRIENDLY_NAME, CONF_HOST, CONF_PORT,
    CONF_COMMAND_OFF, CONF_COMMAND_ON, CONF_SWITCHES, STATE_ON)
import homeassistant.helpers.config_validation as cv
from homeassistant.util import slugify
from homeassistant.helpers.restore_state import RestoreEntity

from pyBrematic.devices.brennenstuhl import RCS1000N
from pyBrematic.devices import Device
from pyBrematic.gateways import BrennenstuhlGateway

REQUIREMENTS = ['pyBrematic==1.0.0']
_LOGGER = logging.getLogger(__name__)

CONF_SYSTEM_CODE = 'system_code'
CONF_UNIT_CODE = 'unit_code'

SWITCH_SCHEMA = vol.Schema({
    vol.Required(CONF_SYSTEM_CODE): cv.string,
    vol.Required(CONF_UNIT_CODE): cv.string,
    vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({    
    vol.Required(CONF_HOST): cv.string,    
    vol.Required(CONF_SWITCHES): cv.schema_with_slug_keys(SWITCH_SCHEMA),
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    host = config[CONF_HOST]

    gateway = BrennenstuhlGateway(host)

    switch_entities = []

    for device, device_config in config[CONF_SWITCHES].items():
        system_code = device_config.get(CONF_SYSTEM_CODE)
        unit_code = device_config.get(CONF_UNIT_CODE)

        brematic_device = RCS1000N(system_code, unit_code)

        switch_entities.append(
            BrematicSwitch(
                device,
                device_config.get(ATTR_FRIENDLY_NAME, device),
                brematic_device,
                gateway
            )
        )

    add_entities(switch_entities)

class BrematicSwitch(SwitchDevice, RestoreEntity):

    def __init__(self, name, friendly_name, switch, gateway):    
        self.entity_id = ENTITY_ID_FORMAT.format(slugify(name))
        self._switch = switch
        self._name = friendly_name
        self._gateway = gateway 

        self._state = None


    async def async_added_to_hass(self):
        """Call when entity about to be added to hass."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state:
          self._state = state.state == STATE_ON

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def should_poll(self):
        """Return True if polling should be used."""
        return False

    @property
    def assumed_state(self):
        """Return True when the current state can not be queried."""
        return False

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._gateway.send_request(self._switch, Device.ACTION_ON)

        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._gateway.send_request(self._switch, Device.ACTION_OFF)

        self._state = False
        self.schedule_update_ha_state()
