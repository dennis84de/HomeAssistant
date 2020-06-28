"""Sensor platform for blueprint."""
from homeassistant.helpers.entity import Entity
from homeassistant import config_entries
from uuid import getnode as get_mac

from .const import (
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN_DATA,
    ICON,
    DOMAIN,
    CONF_DEFAULT_LIST,
    SENSOR_NAME,
)
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    async_add_entities([GkeepSensor(hass, discovery_info)], True)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    async_add_devices([GkeepSensor(hass, config_entry)], True)


class GkeepSensor(Entity):
    """blueprint Sensor class."""

    def __init__(self, hass, config):
        self.config = config
        self.list = config.data.get(CONF_DEFAULT_LIST)
        self.hass = hass
        self.attr = {}
        self._state = None
        self._name = '{}_{}'.format(DEFAULT_NAME, self.list)
        self._unique_id = '{}-{}-{}'.format(get_mac() , SENSOR_NAME, self._name)

    async def async_update(self):
        """Update the sensor."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["gkeep"].update_data()

        # Get new data (if any)
        list = self.hass.data[DOMAIN_DATA]["data"]
        data = []

        # Check the data and update the value.
        if not list or list is None:
            self._state = self._state
        else:
            self._state = len(list.items)
            for item in list.items:
                jitem = {}
                jitem['name'] = item.text
                jitem['checked'] = item.checked
                data.append(jitem)

        # Set/update attributes
        self.attr["attribution"] = ATTRIBUTION
        self.attr["items"] = data

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self._unique_id  

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "Gkeep",
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr
