"""Binary sensor platform for grocy."""
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant import config_entries
from uuid import getnode as get_mac

from .const import (ATTRIBUTION, BINARY_SENSOR_NAME, DEFAULT_NAME, DOMAIN,
                    DOMAIN_DATA, CONF_DEFAULT_LIST)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup binary_sensor platform."""
    async_add_entities(
        [GkeepBinarySensor(hass, discovery_info)], True)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    async_add_devices([GkeepBinarySensor(hass, config_entry)], True)

class GkeepBinarySensor(BinarySensorDevice):
    """grocy binary_sensor class."""

    def __init__(self, hass, config):
        self.config = config
        self.list = config.data.get(CONF_DEFAULT_LIST)
        self.hass = hass
        self.attr = {}
        self._status = False
        self._name = '{}_{}'.format(DEFAULT_NAME, self.list)
        self._unique_id = '{}-{}-{}'.format(get_mac() , BINARY_SENSOR_NAME, self._name)

    async def async_update(self):
        """Update the binary_sensor."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["gkeep"].update_data()

        # Get new data (if any)
        list = self.hass.data[DOMAIN_DATA].get("data", None)
        list_unck = None
        if list is not None:
            list_unck = list.unchecked
        data = []

        # Check the data and update the value.
        if not list_unck or list_unck is None:
            self._status = False
        else:
            self._status = True
            for item in list_unck:
                jitem = {}
                jitem['name'] = item.text
                jitem['checked'] = item.checked
                data.append(jitem)

        # Set/update attributes
        self.attr["attribution"] = ATTRIBUTION
        self.attr["items"] = data

    @property
    def unique_id(self):
        """Return a unique ID to use for this binary_sensor."""
        return self._unique_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "Grocy",
        }

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return self._name

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return None

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self._status

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr

